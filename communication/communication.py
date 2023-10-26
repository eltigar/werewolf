# This module is used in:
# core.py
# actions.py -> action functions for roles

def get_user_id(player):
    return player  # Replace with actual logic to get user_id


def send_to_player(player, message, output_func=print):
    if player != "All":
        user_id = get_user_id(player)  # Replace this with your actual function to get user_id
        output_func(f"{user_id}: {message}")
    else:
        pass
        #  where I have All I must call a cycle


def send_all(num_players, message):
    for player in range(num_players):
        send_to_player(player, message)


def get_from_player(player, prompt, input_func=input):
    send_to_player(player, prompt)
    return input_func()  # Replace this with Telegram API call to get a message if needed


