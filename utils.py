import pickle
from collections import defaultdict

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
