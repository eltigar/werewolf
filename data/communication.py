# communication_old.py
import asyncio


async def send_to_player(player_id: str, message: str):
    from bot import bot

    await bot.send_message(player_id, message)


async def send_multiple(players: list[str], message: str):
    for player_id in players:
        await send_to_player(player_id, message)


async def get_from_player(player_id: str, prompt: str):
    # Отправляем игроку запрос
    await send_to_player(player_id, prompt)

    # Сохраняем состояние игры
    # game_service.game_repo.save_game_state(g) save_game_state()

    # Создаем Future объект для ожидания ввода от пользователя
    return await wait_for_player_input(player_id)




# this does not work if bot is re-started!
awaiting_input = {}


async def wait_for_player_input(user_id):
    future = asyncio.Future()
    awaiting_input[user_id] = future
    try:
        await future
        return future.result()
    finally:
        del awaiting_input[user_id]


def set_player_input(user_id, input_data):
    if user_id in awaiting_input:
        awaiting_input[user_id].set_result(input_data)


# unsuccsessful state managment, future objects must be recreated upon restart
""" 
import pickle
import os

async def wait_for_player_input(user_id):
    filename = 'awaiting_input.pkl'
    # Try to load the existing dictionary, or create a new one if it doesn't exist
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            awaiting_input = pickle.load(file)
    else:
        awaiting_input = {}
    future = asyncio.Future()
    awaiting_input[user_id] = future
    # Save the updated dictionary to the file
    with open(filename, 'wb') as file:
        pickle.dump(awaiting_input, file)
    try:
        await future
        return future.result()
    finally:
        del awaiting_input[user_id]
        # Save the updated dictionary to the file
        with open(filename, 'wb') as file:
            pickle.dump(awaiting_input, file)



def set_player_input(user_id, input_data):
    filename = 'awaiting_input.pkl'
    with open(filename, 'rb') as file:
        awaiting_input = pickle.load(file)
    if user_id in awaiting_input:
        awaiting_input[user_id].set_result(input_data)
"""
