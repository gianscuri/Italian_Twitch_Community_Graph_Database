import asyncio
import aiohttp
import requests
import json
import pandas as pd
import logging
import os


def get_tasks(session, streamers, clientId):
  tasks = []
  headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Client-Id': clientId
    }
  for username in streamers:

    payload = [{
            "operationName":"ChannelRoot_AboutPanel",
            "variables": {
                "channelLogin":username,
                "skipSchedule":True
                },
            "extensions": {
                "persistedQuery": {
                    "version":1,
                    "sha256Hash":"6089531acef6c09ece01b440c41978f4c8dc60cb4fa0124c9a9d3f896709b6c6"
                    }
                }
            }]
    URL = 'https://gql.twitch.tv/gql'
    tasks.append(session.post(url = URL, headers=headers, data=json.dumps(payload), ssl = False))
  return tasks


async def streams_with_viewer(streamers, clientId):
  results = []

  async with aiohttp.ClientSession() as session:
    
    tasks = get_tasks(session, streamers, clientId)
    responses = await asyncio.gather(*tasks)

    for response in responses:
        try:
            results.append(await response.json())
        except Exception:
            logging.error('Error in user_login: Attempt to decode JSON with unexpected mimetype')
        finally:
            pass
  return results


path = os.path.dirname(__file__)
os.chdir(path)
os.chdir('..\..')
print(os.getcwd())

streamers_df = pd.read_csv('DataProcessing/Streamer_dataset.csv', usecols=['streamer'])
streamers = streamers_df['streamer'].tolist()
print(f'Number of total streamers: {len(streamers)}')

headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
home_url = 'https://www.twitch.tv/'
landing = requests.get(home_url,headers=headers)

z = landing.text.strip()
start = 'clientId="'
end = '",commonOptions='
clientId = z[z.find(start)+len(start):z.rfind(end)].strip()


logging.debug(asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()))
stream_list = asyncio.run(streams_with_viewer(streamers, clientId))


socials_url = {}
for x in stream_list:
    temp = []
    if x[0]['data']['user'] is not None:
        for i in x[0]['data']['user']['channel']['socialMedias']:
            temp.append(i['url'])
        socials_url[x[0]['data']['user']['displayName']] = temp
print(f'Number of available streamers: {len(socials_url.keys())}')


socials_df = pd.DataFrame([socials_url])
socials_df = socials_df.transpose()
socials_df.index.name = 'streamer'
socials_df.columns = ['social_list']
socials_df.to_csv('DataCollection/Twitch_social_link/social_link.csv')