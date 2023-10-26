import pickle
from pprint import pprint

with open('users_data.pkl', 'rb') as file:
    data = pickle.load(file)

pprint(data)

with open('games_data.pkl', 'rb') as file:
    data = pickle.load(file)

pprint(data)
