import requests
import json
from datetime import date

##can use 
# import os
# from dotenv import load_dotenv
# load_dotenv(dotenv_path="./.env")


from airflow.decorators import task
from airflow.models import Variable

API_KEY = Variable.get("API_KEY")
CHANNEL_HANDLE = Variable.get("CHANNEL_HANDLE")
maxResults = 50

@task
def get_playlist_id():
    print("▶ Starting get_playlist_id()...")

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

        ##print(channel_playlistId)
        print(f"✓ Completed get_playlist_id() - Found playlist: {channel_playlistId}")
        return channel_playlistId

    except requests.exceptions.RequestException as e:
        raise e


@task
def get_video_ids(playlistId):
    print(f"▶ Starting get_video_ids() for playlist: {playlistId}")

    video_ids = []

    pageToken = None

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=ContentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"

## For the first run, since we don't have a pagetoken we skip the If pageToken check.
## the while loop goes through a get request on the url and then we use a for loop to grab video ids for each page. 
## if there is a valid pagetoken then we set the pageToken variable equal to the current iteration of nextPageToken from the get request and then we loop through it again
## when we reach the end and there are no more valid nextPageTokens then this breaks the while loop
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
        print(f"✓ Completed get_video_ids() - Retrieved {len(video_ids)} video IDs")
        return video_ids

    
    except requests.exceptions.RequestException as e:
        raise e




@task
def extract_video_data(video_ids):
    print(f"▶ Starting extract_video_data() with {len(video_ids)} video IDs...")
    extracted_data = []

    ##this is a helper function to create a batch list of up to 50 video ids to help extract video data
    def batch_list(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id: video_id + batch_size]


    try:
        total_batches = (len(video_ids) + maxResults - 1) // maxResults
        current_batch = 0

        for batch in batch_list(video_ids, maxResults):
            
            current_batch += 1
            print(f"  Processing batch {current_batch}/{total_batches} ({len(batch)} videos)...")

            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    "video": video_id,
                    "title": snippet['title'],
                    "publishedAt": snippet['publishedAt'],
                    "duration": contentDetails['duration'],
                    "viewCount": statistics.get('viewCount', None), ##not all videos have views, likes, comments available so taking it into account by using get method. if not available then replace value with None
                    "likeCount": statistics.get('likeCount', None),
                    "commentCount": statistics.get('commentCount', None),
                }

                extracted_data.append(video_data)
        print(f"✓ Completed extract_video_data() - Extracted data for {len(extracted_data)} videos")
        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e
    

@task
def save_to_json(extracted_data):
    print(f"▶ Starting save_to_json() with {len(extracted_data)} records...")
    file_path = f"./data/YT_data_{date.today()}.json"

    ##this is context management of how to handle file
    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)
    
    print(f"✓ Completed save_to_json() - Saved to {file_path}")


##__name__ is a special built in variable. When this file is run directly, __name__ is called __main__. This bottom check allows us to only run this script when it is called directly and not imported as a module.
if __name__ == "__main__":
    print("=" * 50)
    print("YouTube Data Extraction Pipeline Started")
    print("=" * 50)

    playlistId = get_playlist_id()
    print()

    video_ids = get_video_ids(playlistId)
    print()

    video_data = extract_video_data(video_ids)
    print()

    save_to_json(video_data)
    print()

    print("=" * 50)
    print("Pipeline Completed Successfully!")
    print("=" * 50)