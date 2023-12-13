# communication.py
from bot import bot
from data import game_service

async def send_to_player(player_id: str, message: str):
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
    return await game_service.wait_for_player_input(player_id)
