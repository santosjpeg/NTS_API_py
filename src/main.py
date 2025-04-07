import vlc
import time
import requests
import json

def handle_menu_options(choice):
    if choice == '1':
        play_radio()

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

    print('[+] Radio Channel Overview SUCCESS')

def print_upcoming_set(json_output):
    next = json_output['next']
    title = next['broadcast_title']
    genre_tmp = [j['value'] for j in next['embeds']['details']['genres']]
    genre_list = ', '.join(map(str,genre_tmp))

    # OUTPUT
    print(f"COMING NEXT: {title}")
    print(f"GENRES: {genre_list}")

def play_radio():
    NTS_CHANNEL_1 = 'https://stream-relay-geo.ntslive.net/stream'
    NTS_CHANNEL_2 = 'https://stream-relay-geo.ntslive.net/stream2'
    with open('example.json','r',encoding='utf-8') as fp:
        json_output = json.loads(fp.read())['results']
        raw_radio = [i for i in json_output]

    radio_channel = ''
    radio_select = ''

    print_current_sets(raw_radio)
    print()
    while(radio_channel != '1' and radio_channel != '2'):
        radio_channel = input("Select radio station 1 or 2: ")

    print("[+] Selection loop successfully exited")

    if radio_channel == '1':
        radio_select = NTS_CHANNEL_1
    elif radio_channel == '2':
        radio_select = NTS_CHANNEL_2
    else:
        print("Invalid usage: select 1 or 2")

    player = vlc.MediaPlayer(radio_select)
    radio_output = raw_radio[int(radio_channel) - 1]
    print("[+] Player successfully initialized")
    print()
    player.play()
    time.sleep(1)
    print_upcoming_set(radio_output)
    input("Press enter to stop")
    player.stop()
    print("[+] Successfully exiting radio...")

def main():

    with open('example.json','w', encoding='utf-8') as fp:
        r = requests.get('https://www.nts.live/api/v2/live')
        if(r.status_code == 200):
            print('[+] HTTP GET on nts.live/radio SUCCESS')
            fp.write(json.dumps(r.json(), indent=2))
            print('[+] Write to example.json SUCCESS')



    MENU_OPTIONS = {'1','2','3'}
    menu_primitive = -1 
    while(True):
        print("Welcome to NTS Radio tools.")
        print("(1) 24/7 Radio Channels")
        print("(2) Search Archived Mixes")
        print("(3) Explore Infinite Mixtapes")
        print("(exit) Ends Program")

        menu_primitive = input("Enter valid menu options: ")
        if menu_primitive == 'exit':
            break
        if menu_primitive not in MENU_OPTIONS:
            print("Invalid Option: Choose from {1,2,3,exit}")
        else:
            handle_menu_options(menu_primitive)

if __name__ == '__main__':
    main()
