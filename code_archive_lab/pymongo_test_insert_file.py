import pandas as pd
from app.utils import load_dict
# Get the database using the method we defined in pymongo_test_insert file
from pymongo_get_database import get_database

dbname = get_database()
collection_name = dbname["scripts"]

data = pd.read_csv('data/huberman_videos.csv', encoding='latin1', index_col=False)

items = []
for video_key in data.iloc[1:3]["video_key"]:

    with open(f'data/documents/{video_key}.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()  # each line becomes an element in the list
        # Remove trailing newlines if needed
        lines = [line.strip() for line in lines]

    item_1 = {
    "_id" : data['video_key'][n],
    "episode_num" : n,
    "title" : data['title'][n],
    "transcript" : lines
    }
    items.append(item_1)

collection_name.insert_many(items)

