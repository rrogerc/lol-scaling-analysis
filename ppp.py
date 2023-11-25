import requests

# Start a session to maintain cookies
session = requests.Session()

# Visit the main page to initialize the session
main_page_url = 'https://lolalytics.com/lol/aurelionsol/build/?tier=master'
session.get(main_page_url)

# URL extracted from the network tab for the JSON data
data_url = 'https://ax.lolalytics.com/mega/?ep=champion&p=d&v=1&patch=13.23&cid=136&lane=default&tier=master&queue=420&region=all'

# Use the session to get the JSON data
response = session.get(data_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response JSON content
    data = response.json()
    # Use 'data' as needed
    print(data)
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
