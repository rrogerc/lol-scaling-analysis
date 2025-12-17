import re
import json
import asyncio
import aiohttp
import os
import sys

# Base headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def get_champion_slugs(html_content):
    # Extract the JSON object from the script tag
    match = re.search(r'<script type="qwik/json">(.*?)</script>', html_content, re.DOTALL)
    if not match:
        return []
    
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    objs = data.get('objs', [])
    
    def resolve(idx_str):
        if isinstance(idx_str, str):
            if idx_str.startswith('\u0012'):
                return resolve(idx_str[1:])
            if idx_str.startswith('\u0011'):
                content = idx_str[1:]
                parts = content.split(' ')
                ref = parts[0]
                if ref.endswith('!'):
                    ref = ref[:-1]
                return resolve(ref)
        try:
            idx = int(idx_str, 36)
            if idx < len(objs):
                res = objs[idx]
                if isinstance(res, str) and (res.startswith('\u0012') or res.startswith('\u0011')):
                    return resolve(res)
                return res
        except ValueError:
            pass
        return idx_str

    # Find the champions list object
    # We look for object with 'champions' key
    champions_list = {}
    for obj in objs:
        if isinstance(obj, dict) and 'champions' in obj and 'champTitles' in obj:
            champions_ref = obj['champions']
            champions_list = resolve(champions_ref)
            break
            
    if isinstance(champions_list, dict):
        return list(champions_list.keys())
    
    return []

async def fetch_champion_data(session, champion, tier, patch):
    url = f"https://lolalytics.com/lol/{champion}/build/?tier={tier}&patch={patch}"
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                print(f"Error fetching {champion} (Tier: {tier}, Patch: {patch}): {response.status}")
                return None
            content = await response.text()
            return content
    except Exception as e:
        print(f"Exception fetching {champion} (Tier: {tier}, Patch: {patch}): {e}")
        return None

def extract_time_stats(html_content, champion):
    match = re.search(r'<script type="qwik/json">(.*?)</script>', html_content, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

    objs = data.get('objs', [])
    
    # Simple resolution cache for this document to avoid infinite recursion loops
    memo = {}

    def resolve(idx_str):
        if idx_str in memo:
            return memo[idx_str]
        
        # Base case
        res = idx_str
        
        if isinstance(idx_str, str):
            if idx_str.startswith('\u0012'):
                res = resolve(idx_str[1:])
            elif idx_str.startswith('\u0011'):
                content = idx_str[1:]
                parts = content.split(' ')
                ref = parts[0]
                if ref.endswith('!'):
                    ref = ref[:-1]
                res = resolve(ref)
            else:
                try:
                    idx = int(idx_str, 36)
                    if idx < len(objs):
                        val = objs[idx]
                        if isinstance(val, str) and (val.startswith('\u0012') or val.startswith('\u0011')):
                            res = resolve(val)
                        else:
                            res = val
                except ValueError:
                    pass
        
        memo[idx_str] = res
        return res

    # Find main data object. It usually contains 'sidebar' key.
    main_data = None
    for obj in objs:
        if isinstance(obj, dict) and 'sidebar' in obj and 'summary' in obj:
            main_data = obj
            break
    
    if not main_data:
        return None

    try:
        sidebar = resolve(main_data['sidebar'])
        if isinstance(sidebar, dict) and 'time' in sidebar:
            time_data = resolve(sidebar['time'])
            
            # Extract time games and wins
            # time_data usually has 'time' (games) and 'timeWin' (wins) keys
            # which point to objects with keys "1", "2", ... "7"
            
            if isinstance(time_data, dict) and 'time' in time_data and 'timeWin' in time_data:
                games_obj = resolve(time_data['time'])
                wins_obj = resolve(time_data['timeWin'])
                
                result = {
                    "champion": champion,
                    "buckets": {}
                }
                
                # Buckets 1 to 7
                for i in range(1, 8):
                    k = str(i)
                    games = resolve(games_obj.get(k, 0))
                    wins = resolve(wins_obj.get(k, 0))
                    
                    # Ensure they are numbers
                    if not isinstance(games, (int, float)): games = 0
                    if not isinstance(wins, (int, float)): wins = 0
                    
                    win_rate = (wins / games * 100) if games > 0 else 0
                    
                    result["buckets"][k] = {
                        "games": games,
                        "wins": wins,
                        "win_rate": round(win_rate, 2)
                    }
                return result
    except Exception as e:
        print(f"Error extraction for {champion}: {e}")
        
    return None

async def main():
    # 0. Load Configuration
    if not os.path.exists('config.json'):
        print("config.json not found. Please create it.")
        return

    with open('config.json', 'r') as f:
        config = json.load(f)

    patches = config.get('patches', [])
    tiers = config.get('tiers', ['emerald_plus'])
    concurrency_limit = config.get('concurrency', 5)

    if not patches or not tiers:
        print("Please specify at least one patch and one tier in config.json")
        return

    # 1. Get list of champions by fetching the index page
    print("Fetching initial page to discover champions...")
    async with aiohttp.ClientSession() as session:
        # We fetch the first patch/tier combo to bootstrap the champion list
        initial_html = await fetch_champion_data(session, "missfortune", tiers[0], patches[0])

    if not initial_html:
        print("Failed to get initial HTML to bootstrap champion list.")
        return

    champions = get_champion_slugs(initial_html)
    print(f"Found {len(champions)} champions.")

    if not champions:
        print("No champions found. Check the bootstrap logic.")
        return
    
    # 2. Iterate through config and fetch data
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(concurrency_limit)
        
        for patch in patches:
            for tier in tiers:
                print(f"\n--- Starting extraction for Patch: {patch}, Tier: {tier} ---")
                
                # Create directory structure: data/{patch}/{tier}/
                output_dir = os.path.join("data", patch, tier)
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, "champion_win_rates.json")
                
                results = []
                
                async def process(champ):
                    async with sem:
                        # print(f"Fetching {champ} [{patch}, {tier}]...")
                        html = await fetch_champion_data(session, champ, tier, patch)
                        if html:
                            data = extract_time_stats(html, champ)
                            if data:
                                results.append(data)
                            else:
                                pass 
                        else:
                            print(f"Failed to fetch {champ}")

                tasks = [process(c) for c in champions]
                await asyncio.gather(*tasks)
                
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)
                
                print(f"Completed {patch}/{tier}. Saved {len(results)} records to {output_file}")

    print("\nAll tasks completed.")

if __name__ == "__main__":
    asyncio.run(main())