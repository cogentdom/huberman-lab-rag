import numpy as np
import os
import pickle
import openai
import redis
# from typing import List
from collections import defaultdict
# from redis.commands.search.query import Query

EMBEDDING_MODEL = "text-embedding-3-small"

# Save the defaultdict to a file
def save_defaultdict(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(dict(data), file)

# Load the defaultdict from the file
def load_defaultdict(filename):
    with open(filename, 'rb') as file:
        loaded_dict = pickle.load(file)
        restored_dict = defaultdict(lambda: defaultdict(list), loaded_dict)
    return restored_dict

