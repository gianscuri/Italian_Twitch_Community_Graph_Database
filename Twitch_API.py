import asyncio
import aiohttp
import requests
import json
import pandas as pd
import datetime

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
  num_stream = len(tot)

  print(f'Numero di stream online: {num_stream}') # Numero di stream online
  return tot, num_stream

def get_tasks(session):
  tasks = []

  streamer_list = [tot[i]['user_name'] for i in range(num_stream)]
  #streamer_list = streamer_list[0:100]

  for streamer in streamer_list:
    URL = f'https://tmi.twitch.tv/group/user/{streamer.lower()}/chatters'
    tasks.append(session.get(url = URL, ssl = False))

  return tasks

results = []
async def streams_with_viewer(tot, num_stream):

  async with aiohttp.ClientSession() as session:
    streamer_list = [tot[i]['user_name'] for i in range(num_stream)]
    #stream_dict = {}

    #for streamer in streamer_list:
      #URL = f'https://tmi.twitch.tv/group/user/{streamer.lower()}/chatters'
      #response = await session.get(url = URL, ssl = False)
      #response.raise_for_status() #check for bad response
      #response = await response.json()
    tasks = get_tasks(session)
    responses = await asyncio.gather(*tasks)

    for response in responses:
      results.append(await response.json())
    #  stream_dict[streamer] = {}
    #  stream_dict[streamer]['spect'] = response['chatters']['vips'] + response['chatters']['moderators'] + response['chatters']['viewers']
      #stream_dict[streamer]['game_name'] = list(filter(lambda person: person['user_name'] == streamer, tot))[0]['game_name']
      #stream_dict[streamer]['viewer_count'] = list(filter(lambda person: person['user_name'] == streamer, tot))[0]['viewer_count']

  return results

def save_file(dict):
  filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

  #with open(f'Data/Viewers/{filename}.txt', 'x') as writefile:
  with open(f'c:/Users/gianl/Desktop/Uni Bicocca/GitHub/Twitch_Community_Graph/files/prova.txt', 'w') as writefile:
    writefile.write(dict)


#MAIN
client_id, client_secret = load_keys()
access_token = request_access_token(client_id, client_secret)
tot, num_stream = all_active_streams(client_id, access_token)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) #serve per non far uscire un errore
dict = asyncio.run(streams_with_viewer(tot, num_stream))



save_file(str(dict))
