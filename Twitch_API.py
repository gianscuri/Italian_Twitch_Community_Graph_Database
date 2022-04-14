import asyncio
import aiohttp
import requests
import json
import datetime

def load_keys():
  file_keys = open("twitch_api_keys.txt", "r")
  content = file_keys.readlines()
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

  for i in range(200):  ## Creazione lista di dizionari con tutti gli streamer (max 20000 streamer)
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

def stream_details(tot, num_stream):
  user_login = [tot[i]['user_login'] for i in range(num_stream)]
  user_name = [tot[i]['user_name'] for i in range(num_stream)]
  game_name = [tot[i]['game_name'] for i in range(num_stream)]
  viewer_count = [tot[i]['viewer_count'] for i in range(num_stream)]
  return user_name, user_login, game_name, viewer_count

def get_tasks(session, user_login):
  tasks = []

  for login in user_login:
    URL = f'https://tmi.twitch.tv/group/user/{login}/chatters'
    tasks.append(session.get(url = URL, ssl = False))

  return tasks

async def streams_with_viewer(user_login):
  results = []

  async with aiohttp.ClientSession() as session:
    
    tasks = get_tasks(session, user_login)
    responses = await asyncio.gather(*tasks)

    for response in responses:
      results.append(await response.json())
  return results

def create_dict(stream_list, user_name, game_name, viewer_count):
  stream_dict = {}
  tot_spect_number = 0
  for i in range(len(user_name)):
    stream_dict[user_name[i]] = {}
    stream_dict[user_name[i]]['spect'] = stream_list[i]['chatters']['viewers']
    stream_dict[user_name[i]]['game_name'] = game_name[i]
    stream_dict[user_name[i]]['viewer_count'] = viewer_count[i]
    tot_spect_number = tot_spect_number + len(stream_dict[user_name[i]]['spect'])
  print(f'Numero di spettatori online: {tot_spect_number}')
  return stream_dict

def save_file(stream_dict):
  filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
  with open(f'files_stream/{filename}.txt', 'w') as writefile:
    writefile.write(json.dumps(stream_dict))


#MAIN
client_id, client_secret = load_keys()
access_token = request_access_token(client_id, client_secret)
tot, num_stream = all_active_streams(client_id, access_token)
user_name, user_login, game_name, viewer_count = stream_details(tot, num_stream)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) #serve per non far uscire un errore
stream_list = asyncio.run(streams_with_viewer(user_login))

stream_dict = create_dict(stream_list, user_name, game_name, viewer_count)
save_file(stream_dict)
