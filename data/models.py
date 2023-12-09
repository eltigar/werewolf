import pickle


class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.current_game_id = None  # placeholder for future
        self.current_game_status = None
        self.game_history = {}

'''
class Game:
    def __init__(self, game_id, admin_id, status='created'):
        self.game_id = game_id
        self.admin_id = admin_id
        self.status = status
        self.awaiting_for = None
        self.participants = {admin_id: None}
        self.setup = {'set_of_cards': []}


class Database:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.filename, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}

    def save_data(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.data, file)
'''