from dotenv import load_dotenv,find_dotenv
from bs4 import BeautifulSoup
import urllib.parse
import vlc
import time
import requests
import json
import os

load_dotenv(find_dotenv())

def display_menu_options():
    print("Welcome to NTS Radio tools.")
    print("(1) 24/7 Radio Channels")
    print("(2) Search Archived Mixes")
    print("(3) Explore Infinite Mixtapes")
    print("(exit) Ends Program")

def handle_menu_options(choice):
    if choice == '1':
        play_radio()
    elif choice == '2':
        search_archive()
    elif choice =='3':
        search_infinite_mixtapes()
    else:
        print("Invalid Option: Choose from {1,2,3,exit}")

def extract_track_id(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    meta_tag = soup.find('meta',attrs={'property': 'twitter:player'})
    if not meta_tag:
        return None 

    embed_url = meta_tag['content']
    parsed = urllib.parse.urlparse(embed_url)
    params = urllib.parse.parse_qs(parsed.query)

    api_url = params.get('url', [None])[0]
    if not api_url:
        return None

    track_id = api_url.rstrip('/').split('/')[-1]
    return track_id

def handle_search_options(option, search_results):
    option = int(option) - 1 
    if option not in range(0,12):
        print("INVALID OPTION; Select from 1 to 12")
        return
    json_select = search_results[option]
    url_to_scrape = json_select['audio_sources'][0]['url']

    CLIENT_ID=os.environ.get("CLIENT_ID").strip()
    TRACK_ID = extract_track_id(url_to_scrape)
    
    ATTEMPTS = 3
    for attempt in range(ATTEMPTS):
        try:
            API_URL = f"https://api-v2.soundcloud.com/tracks/{TRACK_ID}?client_id={CLIENT_ID}"
            r = requests.get(API_URL)
            if r.status_code == 200:
                transcodings = r.json().get("media", {}).get("transcodings", [])
                for t in transcodings:
                    if t.get("format", {}).get("protocol") == "progressive":
                        track_api_url = f"{t['url']}?client_id={CLIENT_ID}"
                        print("PROG. TRANSCODING FOUND")
                        break
                else:
                    print("No progressive stream found.")
                    time.sleep(2)
                stream_url_tmp = requests.get(track_api_url).json()
                stream_url = stream_url_tmp.get("url")
                if(stream_url):
                    player = vlc.MediaPlayer(stream_url)
                    player.play()
                    input("Press 'enter' to stop playing.")
                    player.stop()
                    return
                else:
                    print("No URL Response Found")
                    time.sleep(2)
            else:
                print("Failed to call API")
                time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}, attempt {attempt + 1} of {ATTEMPTS}")
            time.sleep(2)

    print("API Request fails after 3 attempts.")
    return

def print_current_sets(raw_radio):
    for i in raw_radio:
        details = i['now']['embeds']['details']
        name = details['name']
        desc = details['description']
        genre_tmp = [j['value'] for j in details['genres']]
        genre_list = ', '.join(map(str,genre_tmp))
        
        print("CHANNEL " + i["channel_name"] + " CURRENTLY PLAYING: " + name)
        print("DESCRIPTION: " + desc)
        print("GENRES: " + genre_list)

def print_upcoming_set(json_output):
    next = json_output['next']
    title = next['broadcast_title']
    genre_tmp = [j['value'] for j in next['embeds']['details']['genres']]
    genre_list = ', '.join(map(str,genre_tmp))

    # OUTPUT
    print(f"COMING NEXT: {title}")
    print(f"GENRES: {genre_list}")


def search_archive():
    API_LATEST = 'https://www.nts.live/api/v2/collections/recently-added'
    with open('latest.json','w', encoding='utf-8') as fp:
        r = requests.get(API_LATEST)
        if(r.status_code == 200):
            fp.write(json.dumps(r.json(), indent=2))
        else:
            print("ERROR: Failed to perform GET Request")
            return
    
    with open('latest.json','r', encoding='utf-8') as fp:
        json_output = json.loads(fp.read())['results']
        all_results = [i for i in json_output]

    user_search = ''

    print("RECENTLY ADDED SHOWS:")
    i = 0
    for i in range(len(all_results)):
        print(f"{i+1}. {all_results[i]['name']}")
    print("(exit) exit")

    while(True):
        user_search = input("Enter menu option: ")
        if user_search == 'exit':
            break
        handle_search_options(user_search, all_results)

def search_infinite_mixtapes():
    pass

def play_radio():
    API_RADIO = 'https://www.nts.live/api/v2/live'
    with open('radio.json','w', encoding='utf-8') as fp:
        r = requests.get(API_RADIO)
        if(r.status_code == 200):
            fp.write(json.dumps(r.json(), indent=2))
        else:
            print("ERROR: Failed to perform GET Request")
            return

    NTS_CHANNEL_1 = 'https://stream-relay-geo.ntslive.net/stream'
    NTS_CHANNEL_2 = 'https://stream-relay-geo.ntslive.net/stream2'
    with open('radio.json','r',encoding='utf-8') as fp:
        json_output = json.loads(fp.read())['results']
        raw_radio = [i for i in json_output]

    radio_channel = ''
    radio_select = ''

    print_current_sets(raw_radio)
    print()
    while(radio_channel != '1' and radio_channel != '2'):
        radio_channel = input("Select radio station 1 or 2: ")

    if radio_channel == '1':
        radio_select = NTS_CHANNEL_1
    elif radio_channel == '2':
        radio_select = NTS_CHANNEL_2
    else:
        print("Invalid usage: select 1 or 2")

    player = vlc.MediaPlayer(radio_select)
    radio_output = raw_radio[int(radio_channel) - 1]
    player.play()
    time.sleep(1)
    print_upcoming_set(radio_output)
    input("Press enter to stop")
    player.stop()

def main():
    menu_primitive = -1 
    while(True):
        display_menu_options()
        menu_primitive = input("Enter valid menu options: ")
        if menu_primitive == 'exit':
            break
        handle_menu_options(menu_primitive)

if __name__ == '__main__':
    main()
