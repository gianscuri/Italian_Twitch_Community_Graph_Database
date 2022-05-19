import asyncio
import aiohttp
import requests
import json
import datetime
import logging
import multiprocessing
import os

path = os.path.dirname(__file__)
logfile = f'{path}\Twitch_stream_collection.log'

#LOGGING
#correct execution
logging.basicConfig(filename= logfile, level =logging.INFO, format= '%(asctime)s,%(levelname)s,%(message)s')
#errors
logging.basicConfig(filename= logfile, level =logging.ERROR, format= '%(asctime)s:%(levelname)s:%(message)s')
#diagnostic
logging.basicConfig(filename= logfile, level =logging.DEBUG, format= '%(asctime)s:%(levelname)s:%(message)s')


def load_keys():
    
  file_keys = open(f"{path}\Twitch_API_keys.txt", "r")
  content = file_keys.readlines()
  logging.info('1,Caricamento chiavi di accesso')
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
  #write message on log file
  logging.info('2,Numero di stream online: {}'.format(num_stream))
  return tot, num_stream

def stream_details(tot, num_stream):
  user_login = []
  user_name = []
  game_name =[]
  viewer_count = []
    
  for i in range(num_stream):
    user_login.append(tot[i]['user_login'])
    user_name.append(tot[i]['user_name'])
    game_name.append(tot[i]['game_name'])
    viewer_count.append(tot[i]['viewer_count'])
   
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
        try:
            results.append(await response.json())
        except Exception:
            logging.error('Error in user_login: Attempt to decode JSON with unexpected mimetype')
        finally:
            pass
            
            
       
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
  #write message on log file
  logging.info('3,Numero di spettatori online: {}'.format(tot_spect_number))
  return stream_dict

def save_file(stream_dict):
    
  filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

  try:
        with open(f'{path}\Files_stream\{filename}.json', 'w') as writefile:
            writefile.write(json.dumps(stream_dict))
        logging.info('4,file {} salvato'.format(filename))
        
  except IOError:
    
    logging.error('Unable to create file on disk')
    
  finally: 
    
    writefile.close()
    


def main():
    client_id, client_secret = load_keys()
    access_token = request_access_token(client_id, client_secret)
    tot, num_stream = all_active_streams(client_id, access_token)
    user_name, user_login, game_name, viewer_count = stream_details(tot, num_stream)
    logging.debug(asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()))
    stream_list = asyncio.run(streams_with_viewer(user_login))
    stream_dict = create_dict(stream_list, user_name, game_name, viewer_count)
    save_file(stream_dict)
        
        

if __name__ == '__main__':
    
     # Start main as a process
    p = multiprocessing.Process(target=main, name="Main", args=())
    p.start()

    # Wait 270 seconds for main
    p.join(timeout=270)
        
    
    #if the process is still running kill it and log timeout error
    if p.is_alive():
        p.terminate()
        logging.error('Esecuzione terminata per Timeout')
        

   