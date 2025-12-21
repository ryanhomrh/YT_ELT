import requests
import json

##can use 
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"

def get_playlist_id():

    try:

        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)

        response.raise_for_status()


        data = response.json()

        ##print(data)

        ##print(json.dumps(data, indent=4))

        ##nested dictionary and lists. Slicing deeper to get to desired values
        ##print(data["items"][0])
        ##print(data["items"][0]["contentDetails"])
        ##print(data["items"][0]["contentDetails"]["relatedPlaylists"])
        ##print(data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])

        channel_items = data["items"][0]

        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        print(channel_playlistId)

        return channel_playlistId

    except requests.exceptions.RequestException as e:
        raise e

##__name__ is a special built in variable. When this file is run directly, __name__ is called __main__. This bottom check allows us to only run this script when it is called directly and not imported as a module.
if __name__ == "__main__":
    get_playlist_id()