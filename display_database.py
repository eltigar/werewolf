import pickle
from pprint import pprint
from data.models import User


def display_object_attributes(obj):
    # Filter out magic attributes and methods
    attributes = [attr for attr in dir(obj) if not attr.startswith('__')]
    for attribute in attributes:
        # Get the value of each attribute
        value = getattr(obj, attribute)
        print(f"{attribute} = {value}")


def display_pickle_content(file_name):
    try:
        with open(file_name, 'rb') as file:
            data = pickle.load(file)
            pprint(data)

            # Check if the data is a dictionary
            if isinstance(data, dict):
                for key, user_object in data.items():
                    print(f"\nUser ID: {key}")
                    display_object_attributes(user_object)
            else:
                # If data is not a dictionary, directly display its attributes
                display_object_attributes(data)
    except Exception as e:
        print(f"An error occurred: {e}")


def display(name):
    with open(name, 'rb') as file:
        my_objects = pickle.load(file)
    print(my_objects)
    # attributes = data
    # for attribute, value in attributes.items():
    #    print(attribute, "=", value)

show = 3
if show == 1: name = 'users.pkl'
elif show == 2: name = 'started_games.pkl'
elif show == 3: name = 'created_games.pkl'
elif show == 4: name = 'canceled_and_aborted_games.pkl'

if __name__ == '__main__':
    display_pickle_content(name)

"""
with open('OLD_games_data.pkl', 'rb') as file:
    data = pickle.load(file)

pprint(data)
"""