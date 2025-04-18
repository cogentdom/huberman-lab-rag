import pandas as pd
# Get the database using the method we defined in pymongo_test_insert file
from pymongo_get_database import get_database

dbname = get_database()
collection_name = dbname["scripts"]

data = pd.read_csv('data/youtube-extract-huberman.csv', encoding='latin1', index_col=False)

n = 1
items = []
for video_id in data.iloc[1:3]["Video ID"]:

    with open(f'data/documents/{video_id}.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()  # each line becomes an element in the list
        # Remove trailing newlines if needed
        lines = [line.strip() for line in lines]

    item_1 = {
    "_id" : data['Video ID'][n],
    "episode_num" : n,
    "title" : data['title'][n],
    "transcript" : lines
    }
    items.append(item_1)
    n+=1

collection_name.insert_many(items)

