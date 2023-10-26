# database.py
import pickle
import uuid


class Database:
    def __init__(self, users_data_filename='users_data.pkl', games_data_filename='games_data.pkl'):
        self.users_data_filename = users_data_filename
        self.users_data = self.load_users_data()

        self.games_data_filename = games_data_filename
        self.games_data = self.load_games_data()

    def save_users_data(self):
        with open(self.users_data_filename, 'wb') as file:
            pickle.dump(self.users_data, file)

    def load_users_data(self):
        try:
            with open(self.users_data_filename, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}

    def save_games_data(self):
        with open(self.games_data_filename, 'wb') as file:
            pickle.dump(self.games_data, file)

    def load_games_data(self):
        try:
            with open(self.games_data_filename, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}

    def add_user(self, user_id, username):
        if user_id not in self.users_data:
            self.users_data[user_id] = {
                'status': None,
                'username': username,
                'game_id': None,
                'game_history': [],
                'total_games': 0,
                'wins': 0
            }


data = Database()


def add_user(user_id, username):
    if user_id not in data.users_data:
        data.users_data[user_id] = {
            'status': None,
            'username': username,
            'game_id': None,
            'game_history': [],
            'total_games': 0,
            'wins': 0
        }
    data.save_users_data()  # Save after adding


def get_user(user_id):
    return data.users_data.get(user_id)


def update_name(user_id, new_name):
    data.users_data[user_id]['username'] = new_name
    data.save_users_data()  # Save after changing


def get_name(user_id):
    return data.users_data[user_id]['username']


def create_new_game(user_id):
    if data.users_data[user_id]['game_id'] is not None:
        return 'Error: already in a game'
    game_id = str(uuid.uuid4())[:8]  # Generating a unique game ID
    game_data = {
        'admin_id': user_id,
        'status': 'created',
        'participants': {
            user_id: {
                'points_earned': None,
            }
        }
    }
    data.games_data[game_id] = game_data
    data.users_data[user_id]['game_id'] = game_id
    data.save_games_data()
    data.save_users_data()
    return f'Successfully created game {game_id}'


def join_game(user_id, game_id):
    existed_game_id = get_game_id_for_user(user_id)
    if existed_game_id is None:
        if game_id in data.games_data:
            data.games_data[game_id]['participants'][user_id] = {'points_earned': None}
            data.users_data[user_id]['game_id'] = game_id
            data.save_games_data()
            data.save_users_data()
            return f'Successfully joined the game {game_id}'
        else:
            return f'Error: game {game_id} not found'
    elif existed_game_id == game_id:
        return f'Error: already in this game'
    else:
        return f'Error: already in the other game'


def leave_game(user_id):
    game_id = get_game_id_for_user(user_id)
    if game_id is None:
        return 'Error: You are not part of any game.'
    elif data.games_data[game_id]['admin_id'] == user_id:
        return 'Error: admin cannot leave'
    else:
        del data.games_data[game_id]['participants'][user_id]
        data.users_data[user_id]['game_id'] = None
        data.save_games_data()
        data.save_users_data()
        return 'Success, you have left the game'


def cancel_game(user_id, game_id):
    if is_admin(user_id, game_id):
        for participant in data.games_data[game_id]['participants']:
            data.users_data[participant]['game_id'] = None
        data.games_data[game_id]['participants'] = {}  # Remove participants
        data.games_data[game_id]['status'] = 'cancelled'  # Set game status to cancelled
        return f'Game successfully cancelled'
    elif game_id is None:
        return f'You are not part of any game.'
    else:
        return f'You are not an admin of the game {game_id}'


def kick_player(user_id_to_kick, admin_id):
    game_id = get_game_id_for_user(user_id_to_kick)
    if is_admin(admin_id, game_id):
        if game_id is not None and user_id_to_kick in data.games_data[game_id]['participants']:
            del data.games_data[game_id]['participants'][user_id_to_kick]
            data.users_data[user_id_to_kick]['game_id'] = None
            data.save_games_data()
            data.save_users_data()
            return f"Player with ID {user_id_to_kick} has been kicked."
        else:
            return f"Failed to kick player with ID {user_id_to_kick}."
    else:
        return f"Failed to kick player: you are not admin."


def get_participants(game_id):
    participants = list(data.games_data[game_id]['participants'])
    return participants


def set_cards(game_id, cards):
    if game_id in data.games_data:
        data.games_data[game_id]['cards'] = cards
        data.save_games_data()
        return f"Cards for the game {game_id} are now set to {cards}."
    return f"Error: game {game_id} not found"


def get_game_id_for_user(user_id):
    return data.users_data[user_id]['game_id']


def is_admin(user_id, game_id):
    if game_id not in data.games_data:
        return False
    return data.games_data[game_id]['admin_id'] == user_id
