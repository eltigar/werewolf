# This module is used in:
# core.py
# actions.py -> action functions for roles
# from bot import send_message_via_aiogram
# from data import started_games
# from data.models import Game

"""

class GameState:
    def __init__(self, game_id, num_players):
        self.game_id = game_id
        self.num_players = num_players
        self.status = None
        self.answer = None
        self.votes = {}

    def add_vote(self, user_id, vote):
        self.votes[user_id] = vote

    def await_for(self, user_id):
        self.status = user_id

    def start_voting(self):
        self.status = 'voting'


games_statuses = {}
for saved_game in started_games:
    games_statuses[saved_game.game_id] = GameState(saved_game.game_id, len(saved_game.participants))
    games_statuses[saved_game.game_id].votes = saved_game.votes


def check_if_game_can_start(game: Game):
    game_id = game.game_id
    num_players = len(game.participants)
    game_state = GameState(game_id, num_players)
"""

def get_user_id(player):
    return player  # Replace with actual logic to get user_id


async def async_print(message):
    print(message)


def send_to_player(player, message, output_func=print):
    if player != "All":
        user_id = get_user_id(player)
        output_func(f"{user_id}: {message}")
    else:
        send_all(num_players, message)


def send_all(num_players, message):
    for player in range(num_players):
        send_to_player(player, message)


def get_from_player(player, prompt, input_func=input):
    send_to_player(player, prompt)
    # started_games.data
    return input_func()  # Replace this with Telegram API call to get a message if needed


def get_from_telegram(text):
    return text
