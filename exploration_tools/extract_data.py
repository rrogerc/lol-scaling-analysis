import json
import re
import sys

def extract_json():
    with open('lolalytics_mf.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to capture the JSON content inside the script tag
    match = re.search(r'<script type="qwik/json">(.*?)</script>', content, re.DOTALL)
    if not match:
        print("Could not find qwik/json script tag.")
        return

    json_str = match.group(1)
    
    # Qwik JSON can have escaped characters that standard json.loads might dislike if not careful, 
    # but usually it's valid JSON.
    # There might be some control characters like \u0012? 
    # The snippet showed "\u0012a8". This is a Qwik serialization marker.
    # We might need to handle that, but let's try json.loads first.
    # Qwik replaces some values with strings starting with \u0012 (ASCII 18). 
    # This indicates a reference or a special type. 
    # However, json.loads should handle the string itself fine.
    
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # Sanitize common issues if any
        return

    objs = data.get('objs', [])
    
    # Helper to resolve hex index
    def resolve(idx_str):
        if isinstance(idx_str, str):
            if idx_str.startswith('\u0012'):
                return resolve(idx_str[1:])
            if idx_str.startswith('\u0011'):
                # Handle \u0011 prefix and potential space separation
                # e.g. "\u00118rn! @4t" -> resolve("8rn")
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
                # If result is a reference string, resolve it too
                if isinstance(res, str) and (res.startswith('\u0012') or res.startswith('\u0011')):
                    return resolve(res)
                return res
        except ValueError:
            pass
        return idx_str # Return as is if not resolvable

    # Find object containing "wrlchart"
    target_obj = None
    for obj in objs:
        if isinstance(obj, dict) and 'wrlchart' in obj:
            target_obj = obj
            break
    
    if not target_obj:
        print("Could not find object with 'wrlchart' key.")
        return

    print(f"Found container object: {target_obj}")
    
    wrlchart_ref = target_obj['wrlchart']
    print(f"wrlchart ref: {wrlchart_ref}")
    
    # Debug indices around 9qc
    indices = ['9qc', '9qd', '9qe', '9qf', '9qg', '9qh', '9qi', '9qj']
    for idx_str in indices:
        val = resolve(idx_str)
        print(f"Index {idx_str} ({int(idx_str, 36)}): {val}")

    # Search for object with type that matches 'wrlchart' string index
    # We found 'wrlchart' string at 9qc.
    # So we look for obj where obj['type'] == '9qc' or similar.
    
    wrlchart_str_idx = '9qc' 
    
    found_chart_obj = None
    for i, obj in enumerate(objs):
        if isinstance(obj, dict) and obj.get('type') == wrlchart_str_idx:
            print(f"Found chart object at index {i}: {obj}")
            found_chart_obj = obj
            # Continue searching to see if there are others
            
    # Also look for the pattern {"type":"9qf","$$data":"9qg"} seen in grep
    # If 9qf points to "wrlchart" string?
    
    wrlchart_key_idx = None
    for i, obj in enumerate(objs):
        if obj == "wrlchart":
            wrlchart_key_idx = i
            # simple base36 conversion for display
            def base36encode(number):
                if not isinstance(number, int):
                    return ""
                alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
                base36 = ''
                sign = ''
                if number < 0:
                    sign = '-'
                    number = -number
                if 0 <= number < len(alphabet):
                    return sign + alphabet[number]
                while number != 0:
                    number, i = divmod(number, len(alphabet))
                    base36 = alphabet[i] + base36
                return sign + base36

            print(f"String 'wrlchart' found at index {i} (base36: {base36encode(i)})")
            
            # Now find object that uses this index as type
            b36_idx = base36encode(i)
            for j, o in enumerate(objs):
                if isinstance(o, dict) and o.get('type') == b36_idx:
                     print(f"Found object referencing 'wrlchart' (index {b36_idx}) at index {j}: {o}")
                     if '$$data' in o:
                         chart_data = resolve(o['$$data'])
                         # Recursively resolve if the data itself contains $$data
                         while isinstance(chart_data, dict) and '$$data' in chart_data:
                             print(f"Resolving nested $$data: {chart_data['$$data']}")
                             chart_data = resolve(chart_data['$$data'])
                         
                         print("Chart Data:")
                         print(json.dumps(chart_data, indent=2))

    # Resolving 7ry which is the main data object
    main_data = resolve('7ry')
    
    # In previous thoughts, we saw "champions":"fd" in object 17f (which was tips or strings?)
    # Let's find object that has "champions" key.
    
    champions_list = None
    
    for i, obj in enumerate(objs):
        if isinstance(obj, dict) and 'champions' in obj and 'champTitles' in obj:
            print(f"Found config object at index {i}: {obj}")
            if 'champions' in obj:
                champions_ref = obj['champions']
                print(f"Champions ref: {champions_ref}")
                champions_list = resolve(champions_ref)
                # print(json.dumps(champions_list, indent=2))
                if isinstance(champions_list, dict):
                    print(f"Found {len(champions_list)} champions.")
                    # Print first 5 items to verify structure
                    keys = list(champions_list.keys())[:5]
                    for k in keys:
                        print(f"{k}: {champions_list[k]}")
            break

if __name__ == '__main__':
    extract_json()

if __name__ == '__main__':
    extract_json()
