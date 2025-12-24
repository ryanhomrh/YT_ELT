import requests
import json

##can use 
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxResults = 50

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


def get_video_ids(playlistId):

    video_ids = []

    pageToken = None

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=ContentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"

## For the first run, since we don't have a pagetoken we skip line 68 of the 
    try:

        while True:
            url = base_url

            if pageToken: ##if pageToken has a not None value type (aka it exists) then append this to the url else break the while loop
                url += f"&pageToken={pageToken}"

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            
            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids

    
    except requests.exceptions.RequestException as e:
        raise e



##__name__ is a special built in variable. When this file is run directly, __name__ is called __main__. This bottom check allows us to only run this script when it is called directly and not imported as a module.
if __name__ == "__main__":
    playlistId = get_playlist_id()
    get_video_ids(playlistId)