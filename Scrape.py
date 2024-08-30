import re
import requests
import json

from Champions import champions, champion_numbers

all_champions_data = {}
tier = "emerald_plus" # emerald_plus, diamond_plus, all
role = "default"  # default, top, jungle, middle, bottom, support
json_filename = f"{tier}.json"
session = requests.Session()

for i in range(champions.__len__()):
    if role == "default":
        data_url = f"https://lolalytics.com/lol/{champions[i].lower()}/build/?tier={tier}&patch=30"
    else:
        data_url = f"https://lolalytics.com/lol/{champions[i].lower()}/build/?lane={role}&tier={tier}&patch=30"
    
    print(data_url)
    response = session.get(data_url)

    if response.status_code != 200:
        print("Failed to retrieve data. Status code: {response.status_code}: " + champions[i])
        continue
    print(f"Processing: {champions[i]} + {champion_numbers[i]}")

    html_content = response.text

    sentinel_position = html_content.find('"timeWin"')

    if sentinel_position != -1:

        line_start = html_content.rfind('\n', 0, sentinel_position)        
        line_end = html_content.find('\n', sentinel_position)
        relevant_content = html_content[line_start + 1: line_end if line_end != -1 else len(html_content)]
    
       
        # Use a regular expression to find the last two sequences of 7 numbers before the sentinel
        pattern = r'(\d{3,6}(?:,\d{3,6}){6})'
        matches = re.findall(pattern, relevant_content)

        # Assuming the last two matches are the ones you want
        if len(matches) >= 2:
            first_array = [int(num) for num in matches[-2].split(",")]
            second_array = [int(num) for num in matches[-1].split(",")]
        else:
            print("Not enough number sequences found.")
            continue
    else:
        print("Sentinel 'timeWin' not found.")
        continue

    # Extract 'timeWin' and 'time' data and calculate winrates
    time_win_data = second_array
    time_data = first_array
    # print("time_win_data:", time_win_data)
    # print("time_data:", time_data)

    # print(len(time_win_data))
    # print(len(time_data))

    sorted_data = [time_win_data / time_data for time_win_data, time_data in zip(time_win_data, time_data)]

    all_champions_data[champions[i]] = sorted_data

with open(json_filename, "w") as file:
    json.dump(all_champions_data, file)

print(f"Data saved to {json_filename}")
