import requests
import json

from Champions import champions, champion_numbers

all_champions_data = {}
json_filename = "diamond_plus.json"
tier = "diamond_plus"
session = requests.Session()

for i in range(champions.__len__()):
    data_url = f"https://ax.lolalytics.com/mega/?ep=champion&p=d&v=1&patch=30&cid={champion_numbers[i]}&lane=default&tier={tier}&queue=420&region=all"
    
    response = session.get(data_url)

    if response.status_code != 200:
        print("Failed to retrieve data. Status code: {response.status_code}: " + champions[i])
        continue

    print(f"Processing: {champions[i]} + {champion_numbers[i]}")

    data = response.json()

    # Extract 'timeWin' and 'time' data and calculate winrates
    time_win_data = data["timeWin"]
    time_data = data["time"]

    winrates = {
        int(key): time_win_data[key] / time_data[key] if time_data[key] != 0 else 0
        for key in time_win_data
    }

    # Sort the data by game length
    sorted_data = sorted(winrates.items())
    sorted_game_lengths, sorted_winrates = zip(*sorted_data)

    all_champions_data[champions[i]] = sorted_winrates

with open(json_filename, "w") as file:
    json.dump(all_champions_data, file)

print(f"Data saved to {json_filename}")
