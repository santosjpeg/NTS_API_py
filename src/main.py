import vlc
import time
import requests
import json

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

def handle_search_options(option):
    print(f"[+] User selected {option}...")
    pass

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
        all_results = [i['name'] for i in json_output]

    user_search = ''

    print("RECENTLY ADDED SHOWS:")
    print("0. SEARCH")
    for i in range(len(all_results)):
        print(f"{i+1}. {all_results[i]}")
    print("(exit) exit")

    while(True):
        user_search = input("Enter menu option: ")
        if user_search == 'exit':
            break
        handle_search_options(user_search)
        

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
