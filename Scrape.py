import requests
from bs4 import BeautifulSoup
import json
import re
import matplotlib.pyplot as plt


champions = [
    'Aatrox', 'Ahri', 'Akali', 'Alistar', 'Amumu', 'Anivia', 'Annie', 'Aphelios', 'Ashe',
    'Aurelion Sol', 'Azir', 'Bard', 'Blitzcrank', 'Brand', 'Braum', 'Caitlyn', 'Camille',
    'Cassiopeia', 'Cho\'Gath', 'Corki', 'Darius', 'Diana', 'Dr. Mundo', 'Draven', 'Ekko',
    'Elise', 'Evelynn', 'Ezreal', 'Fiddlesticks', 'Fiora', 'Fizz', 'Galio', 'Gangplank',
    'Garen', 'Gnar', 'Gragas', 'Graves', 'Gwen', 'Hecarim', 'Heimerdinger', 'Illaoi',
    'Irelia', 'Ivern', 'Janna', 'Jarvan IV', 'Jax', 'Jayce', 'Jhin', 'Jinx', 'Kai\'Sa',
    'Kalista', 'Karma', 'Karthus', 'Kassadin', 'Katarina', 'Kayle', 'Kayn', 'Kennen',
    'Kha\'Zix', 'Kindred', 'Kled', 'Kog\'Maw', 'LeBlanc', 'Lee Sin', 'Leona', 'Lillia',
    'Lissandra', 'Lucian', 'Lulu', 'Lux', 'Malphite', 'Malzahar', 'Maokai', 'Master Yi',
    'Miss Fortune', 'Mordekaiser', 'Morgana', 'Nami', 'Nasus', 'Nautilus', 'Neeko',
    'Nidalee', 'Nocturne', 'Nunu', 'Olaf', 'Orianna', 'Ornn', 'Pantheon',
    'Poppy', 'Pyke', 'Qiyana', 'Quinn', 'Rakan', 'Rammus', 'Rek\'Sai', 'Rell', 'Renekton',
    'Rengar', 'Riven', 'Rumble', 'Ryze', 'Samira', 'Sejuani', 'Senna', 'Seraphine',
    'Sett', 'Shaco', 'Shen', 'Shyvana', 'Singed', 'Sion', 'Sivir', 'Skarner', 'Sona',
    'Soraka', 'Swain', 'Sylas', 'Syndra', 'Tahm Kench', 'Taliyah', 'Talon', 'Taric',
    'Teemo', 'Thresh', 'Tristana', 'Trundle', 'Tryndamere', 'Twisted Fate', 'Twitch',
    'Udyr', 'Urgot', 'Varus', 'Vayne', 'Veigar', 'Vel\'Koz', 'Vi', 'Viego', 'Viktor',
    'Vladimir', 'Volibear', 'Warwick', 'Wukong', 'Xayah', 'Xerath', 'Xin Zhao', 'Yasuo',
    'Yone', 'Yorick', 'Yuumi', 'Zac', 'Zed', 'Zeri', 'Ziggs', 'Zilean', 'Zoe', 'Zyra'
]

all_champions_data = {}

for champion in champions:
    boy = re.sub(r'[^a-zA-Z0-9]', '', champion).lower()

    # Fetch the web page
    url = f'https://lolalytics.com/lol/{boy}/build/?tier=1trick&patch=30'
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the script tag containing the 'precache' variable
    script = soup.find('script', string=re.compile(r'var precache ='))

    if (script is None):
        print(f'No script tag found for {boy}')
        continue
    print(f'Processing: {boy}')

    # Extract and process the 'precache' variable content
    precache_string = script.string.split('var precache =')[1].split(';')[0].strip()
    precache_data = json.loads(precache_string)

    header = list(precache_data.keys())[0]

    # Extract 'timeWin' and 'time' data and calculate winrates
    time_win_data = precache_data[header]['timeWin']  # Adjust the key based on the actual data structure
    time_data = precache_data[header]['time']        # Adjust the key based on the actual data structure

    winrates = {int(key): time_win_data[key] / time_data[key] if time_data[key] != 0 else 0 for key in time_win_data}

    # Sort the data by game length
    sorted_data = sorted(winrates.items())
    sorted_game_lengths, sorted_winrates = zip(*sorted_data)

    all_champions_data[champion] = sorted_winrates    

    # Plot
    # plt.figure(figsize=(10, 6))
    # plt.plot(sorted_game_lengths, sorted_winrates, marker='o', linestyle='-', color='b')
    # plt.title("Winrate vs Sorted Game Length")
    # plt.xlabel("Sorted Game Length")
    # plt.ylabel("Winrate")
    # plt.grid(True)
    # plt.show()

print(all_champions_data)

filename = 'onetrick30days_all_champions_data.json'

# Write the data to a file
with open(filename, 'w') as file:
    json.dump(all_champions_data, file)

print(f"Data saved to {filename}")