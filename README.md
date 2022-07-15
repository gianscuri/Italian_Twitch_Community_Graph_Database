# Twitch community graph

## Abstract

[Twitch.tv](https://www.twitch.tv/) is a live streaming platform that allows streamers to broadcast and users to enjoy content in real time. The broadcasts cover various categories related mainly to the world of video games, entertainment, and the arts.
Thanks to its great success, especially in the last few years, both the revenue opportunities for streamers and companies operating in these sectors have increased.
Understanding the market and the platform, however, is crucial to discovering the interests of users.
This project therefore aims to collect and analyze information about the different directs in order to create an explorable and queryable graph model of the communities present thus enabling accurate market analysis.

The project consists of a series of scripts to collect, integrate, analyze and save data from different sources. It is thus a tool that can be run in any time frame to obtain the up-to-date graph of the situation.
The data collection phase is done from two separate sources: [Twitch](https://www.twitch.tv/) for live information and [Steam](https://steamdb.info/graph/) for video game information (a video game distribution site). Collection was done in two distinct ways through the use of APIs and through dynamic scraping techniques. In the processing phase, the datasets containing the streamers, the different video games streamed, and the related bridge-tables that allow them to be linked are then obtained. The streamer-game links were calculated by analyzing the broadcast categories while the streamer-streamer links were calculated by evaluating the rate of common viewers between each pair of streamers.

This repository contains data collected over a two-week period in May 2022 regarding all Italian broadcasts on Twitch and data from SteamDB regarding video games. Approximately 2.5GB of data between streams and video games were collected during this period, which after detailed analysis allowed the creation of a graph model on the Neo4j DBMS consisting of 4121 nodes and 54931 relationships.

## Execution scheme

![Pipeline](https://github.com/gianscuri/Twitch_Community_Graph/blob/main/DataVisualization/Images/pipeline.png)

### Data Collection

1. Request and add Twitch API keys to the file `Twitch_API_keys.txt`
2. Create a repeated execution task for `Twitch_stream_collection.py` every xx minutes (Win: Task Scheduler, Linux: Crontab)
    - choose the language of the desired streams
    - this script saves the collected stream files in individual json files but it's already supported the upload on MongoDB local server, uncomment the import function in the script (it requires [MongoDB Community Server](https://www.mongodb.com/try/download/community))
3. Run `steam_games_scraping.ipynb` to scrape [SteamDB](https://steamdb.info/graph/) website (if the website asks CAPTCHA clean browser cookies)
4. Download bot dataset from [Twitch Insights](https://twitchinsights.net/bots) using a browser extension (e.g. Table Capture for Chrome) and save it as `Twitch_bot_list.csv`
5. Run `Twitch_social_link.py` to obtain the streamer's social link (this can be run only after Data Processing because it needs the complete streamer list)

### Data Processing

1. Run `DataProcessing.ipynb` selecting the parameters for the analysis in the first block:
    - data source (json files or MongoDB local server)
    - set the time interval acquisition (xx minutes)
    - set parameters and thresholds
2. Run `DataEnrichment.ipynb` to add games info from SteamDB (verify manually the matches)
3. Run `DataExploration.ipynb` and `DataQuality.ipynb` to obtain data insights

### Data Modelling

1. Install [Neo4j Community Server](https://neo4j.com/download-center/#community)
2. Copy the CSVs obtained in the `output_datasets` folder into your neo4j import folder (neo4j/import/)
3. Run `graph_neo4j.ipynb` to load data in Neo4j
4. Execute desired queries

### Data Visualization

1. Install Gephi
2. Import `Streamer_dataset_short.csv` and `Streamer-Streamer_dataset_short.csv`
3. Execute the layout algorithm (e.g. Atlas Force), execute statistics analysis to detect communities (e.g. Modularity), edit nodes and edges colors (more details [here](https://github.com/KiranGershenfeld/VisualizingTwitchCommunities))


For additional info on the project read `ProjectReport_ita.pdf` (in Italian)

![Graph visualization on Gephi May 2022](https://github.com/gianscuri/Twitch_Community_Graph/blob/main/DataVisualization/Images/Gephi_graph_dark.png)
