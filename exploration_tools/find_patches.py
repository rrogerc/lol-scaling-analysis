import json
import re

def find_patches():
    with open('lolalytics_mf.html', 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'<script type="qwik/json">(.*?)</script>', content, re.DOTALL)
    if not match:
        print("Could not find qwik/json script tag.")
        return

    json_str = match.group(1)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return

    objs = data.get('objs', [])
    
    # Helper to resolve hex index to value
    def resolve(idx_str):
        if isinstance(idx_str, str):
            # Handle standard references \u0012
            if idx_str.startswith('\u0012'):
                return resolve(idx_str[1:])
            # Handle \u0011 references (often followed by flags)
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
                return objs[idx]
        except ValueError:
            pass
        return idx_str

    print(f"Searching {len(objs)} objects for patch information...")

    # Strategy 1: Look for "15.24" string in objs list directly
    patch_indices = []
    for i, obj in enumerate(objs):
        if isinstance(obj, str) and "15.24" in obj:
            print(f"Found '15.24' at index {i} (base36: {base36encode(i)}): {obj}")
            patch_indices.append(base36encode(i))
    
    # Inspect object 1564
    target_idx = 1564
    if target_idx < len(objs):
        print(f"\nInspecting object {target_idx}:")
        obj = objs[target_idx]
        print(obj)
        if isinstance(obj, dict):
            for k, v in obj.items():
                print(f"  {k}: {resolve(v)}")
                
    # Also check "11v" champPath
    champPath = resolve("11v")
    print(f"\nResolved '11v': {champPath}")

def base36encode(number):
    if not isinstance(number, int):
        return ""
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    base36 = ''
    if 0 <= number < len(alphabet):
        return alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return base36

if __name__ == '__main__':
    find_patches()