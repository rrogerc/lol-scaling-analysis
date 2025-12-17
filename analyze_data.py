import json
import os
import argparse

TIME_LABELS = {
    "1": "0 - 15 min",
    "2": "15 - 20 min",
    "3": "20 - 25 min",
    "4": "25 - 30 min",
    "5": "30 - 35 min",
    "6": "35 - 40 min",
    "7": "40+ min"
}

def load_config():
    if not os.path.exists('config.json'):
        print("config.json not found.")
        return None
    with open('config.json', 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Analyze aggregated champion win rates.")
    parser.add_argument("--top", "-n", type=int, default=10, help="Number of top champions to display per interval.")
    args = parser.parse_args()
    
    top_n = args.top

    config = load_config()
    if not config:
        return

    patches = config.get('patches', [])
    tiers = config.get('tiers', [])

    # Master dictionary to hold aggregated data
    aggregated_data = {}

    print(f"Aggregating data for Patches: {patches} and Tiers: {tiers}...")

    found_files = 0
    
    for patch in patches:
        for tier in tiers:
            file_path = os.path.join("data", patch, tier, "champion_win_rates.json")
            
            if not os.path.exists(file_path):
                print(f"  [Warning] Missing data file: {file_path}")
                continue
            
            found_files += 1
            with open(file_path, 'r') as f:
                file_data = json.load(f)
                
            for entry in file_data:
                champ = entry['champion']
                if champ not in aggregated_data:
                    aggregated_data[champ] = {k: {"games": 0, "wins": 0} for k in TIME_LABELS.keys()}
                
                for bucket_key, stats in entry['buckets'].items():
                    # Accumulate counts
                    aggregated_data[champ][bucket_key]['games'] += stats['games']
                    aggregated_data[champ][bucket_key]['wins'] += stats['wins']

    if found_files == 0:
        print("No data files found to analyze.")
        return

    print(f"Aggregation complete. Analyzed {found_files} files.\n")

    MIN_GAMES = 100 

    # Now calculate winrates and rank for each bucket
    for i in range(1, 8):
        bucket_key = str(i)
        label = TIME_LABELS[bucket_key]
        
        ranking = []
        
        for champ, buckets in aggregated_data.items():
            b_stats = buckets[bucket_key]
            games = b_stats['games']
            wins = b_stats['wins']
            
            if games >= MIN_GAMES:
                win_rate = (wins / games) * 100
                ranking.append((champ, win_rate, games))
        
        ranking.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n=== {label} (Top {top_n}, min {MIN_GAMES} games) ===")
        print(f"{'Rank':<5} {'Champion':<20} {'Win Rate':<10} {'Games':<10}")
        print("-" * 50)
        
        for rank, (champ, wr, games) in enumerate(ranking[:top_n], 1):
            print(f"{rank:<5} {champ:<20} {wr:>5.2f}% {games:>8}")

if __name__ == "__main__":
    main()