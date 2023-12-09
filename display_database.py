import pickle
from pprint import pprint
def display(name='users.pkl'):
    with open(name, 'rb') as file:
        data = pickle.load(file)
    print(data)
    # attributes = data
    # for attribute, value in attributes.items():
    #    print(attribute, "=", value)


if __name__ == '__main__':
    display('created_games.pkl')
"""
with open('OLD_games_data.pkl', 'rb') as file:
    data = pickle.load(file)

pprint(data)
"""