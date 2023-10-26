from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU as LEXICON
from data_storage.data import create_new_game, join_game, leave_game, kick_player, cancel_game,\
    get_game_id_for_user, is_admin, set_cards, get_participants, get_name


# Инициализируем роутер уровня модуля
router = Router()


# Example game setup command handler
@router.message(Command(commands='new'))
async def new_game(message: Message):
    answer = create_new_game(message.from_user.id)
    await message.answer(answer)


@router.message(Command(commands='join'))
async def join_game_command(message: Message):
    game_id = message.text[len('/join '):]  # The format is /join <game_id>
    if not game_id:
        answer = 'Error: you have not entered game ID'
    else:
        answer = join_game(message.from_user.id, game_id)
    await message.answer(answer)


@router.message(Command(commands='leave'))
async def leave_game_command(message: Message):
    answer = leave_game(message.from_user.id)
    await message.answer(answer)


@router.message(Command(commands='kick'))
async def kick_player_command(message: Message):
    user_id_to_kick = message.text[7:]
    if len(user_id_to_kick) < 3:
        await message.answer(f"Error: user ID was not provided")
    else:
        await message.answer(kick_player(user_id_to_kick, message.from_user.id))


@router.message(Command(commands='cancel'))
async def cancel_game_command(message: Message):
    user_id = message.from_user.id
    game_id = get_game_id_for_user(message.from_user.id)
    answer = cancel_game(user_id, game_id)
    await message.answer(answer)


@router.message(Command(commands='set_cards'))
async def set_cards_command(message: Message):
    # Assuming you have a logic to fetch the current game_id for the user sending the message
    game_id = get_game_id_for_user(message.from_user.id)
    if is_admin(message.from_user.id, game_id):
        cards = message.text[11:].split()  # The format is /set_cards card1 card2 card3 ...
        if not cards:
            await message.answer(f"Error: no cards were given")
        else:
            answer = set_cards(game_id, cards)
            await message.answer(answer)
    elif game_id is None:
        await message.answer(f'You are not part of any game.')
    else:
        await message.answer(f"You are not the admin")


@router.message(Command(commands='show_joined'))
async def show_joined_command(message: Message):
    user_id = message.from_user.id
    game_id = get_game_id_for_user(user_id)  # Assuming you have a function to get game_id for a user

    if game_id is None:
        await message.answer("You are not part of any game.")
    else:
        participants = get_participants(game_id)
        for i in range(len(participants)):
            participants[i] = (participants[i], get_name(participants[i]))
        if not participants:
            await message.answer(f"No participants found for game with ID: {game_id}")
        await message.answer(f"Players in game with ID {game_id}:\n{participants}")
