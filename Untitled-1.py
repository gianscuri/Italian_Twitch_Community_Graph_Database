import requests

def load_keys():
    file = open("twitch_api_keys.txt", "r")
    content = file.readlines()
    return content[1].strip(), content[3].strip()


def request_access_token(client_id, client_secret):
    URL = 'https://id.twitch.tv/oauth2/token'
    PARAMS = {'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'}

    response = requests.post(url = URL, params = PARAMS)
    response.raise_for_status() #check for bad response

    response = response.json()
    return response['access_token']


def all_active_streams(client_id, access_token):
    tot = [] # Inizializzazione cose
    page_streamer = {}
    page_streamer['pagination'] = {}
    page_streamer['pagination']['cursor'] = None

    URL = 'https://api.twitch.tv/helix/streams' # Url e head
    HEAD = {'Client-ID' : client_id,
            'Authorization' :  f'Bearer {access_token}'}

    for i in range(100):  ## Creazione lista di dizionari con tutti gli streamer (max 10000 streamer)
        if page_streamer['pagination'] == {}:
            break
        PARAMS = {'language': 'it',
                'first': 100,
                'after': page_streamer['pagination']['cursor']}

        page_streamer = requests.get(url = URL, headers = HEAD, params = PARAMS)
        page_streamer.raise_for_status() #check for bad response
        page_streamer = page_streamer.json()
        tot.extend(page_streamer['data']) 

    print(f'Numero di stream online: {len(tot)}') # Numero di stream online
    return tot



#MAIN
client_id, client_secret = load_keys()
access_token = request_access_token(client_id, client_secret)
tot = all_active_streams(client_id, access_token)