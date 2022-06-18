# Twitch community graph

## Execution scheme

### Data Collection

1. Add Twitch API keys to the file `Twitch_API_keys.txt`
2. Create a repeated execution task for `Twitch_stream_collection.py` every xx minutes (Win: Task Scheduler, Linux: Crontab)
    - choose the language of the desired streams
    - this script saves the collected stream files in individual files but it's already supported the upload on MongoDB local server, uncomment the import function in the script (it requires [MongoDB Community Server](https://www.mongodb.com/try/download/community))
3. Run `steam_games_scraping.ipynb` to scrape [SteamDB](https://steamdb.info/graph/) website (if the website asks CAPTCHA clean browser cookies)
4. Download bot dataset from [Twitch Insights](https://twitchinsights.net/bots) using a browser extension (e.g. Table Capture for Chrome) and save as `Twitch_bot_list.csv`
5. Run `Twitch_social_link.py` to obtain the streamer's social link (this can be run only after Data Processing because it needs the streamer list)

### Data Processing

1. Select the parameter for the analysis in the first block of `DataProcessing.ipynb` file
    - data source (individual files or MongoDB local server)
    - set the time interval acquisition (xx minutes)
    - set parameters and thresholds
2. Run `DataProcessing.ipynb`

### Data Modelling

1. Install [Neo4j Community Server](https://neo4j.com/download-center/#community)
2. Run `graph_neo4j.ipynb` to import data
3. Execute desired queries

### Data Visualization

1. Install Gephi
2. Import `Streamer_dataset_short.csv` and `Streamer-Streamer_dataset_short.csv`
3. Execute one layout algorithm, execute statistics analysis to detect communities, edit nodes and edges colors (more details [here](https://github.com/KiranGershenfeld/VisualizingTwitchCommunities))

![Graph visualization on Gephi May 2022](https://github.com/gianscuri/Twitch_Community_Graph/blob/main/DataVisualization/Images/Gephi_graph_dark.png)
