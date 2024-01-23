from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU as LEXICON

from data import game_service

# Инициализируем роутер уровня модуля
router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON['/start'])
    game_service.user_repo.add_user(str(message.from_user.id), message.from_user.first_name)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON['/help'])


@router.message(Command(commands='change_name'))
async def change_name_command(message: Message):
    user_id = str(message.from_user.id)
    user = game_service.user_repo.get_user(user_id)
    new_name = message.text[13:].strip()
    if user.current_game_id:
        answer = 'You are not allowed to change name in-game'
        await message.answer(answer, parse_mode='Markdown')
    elif len(new_name) == 0:
        answer = LEXICON['/change_name_request']
        await message.answer(answer, parse_mode='Markdown')
        await message.answer(text=f"Ваше текущее имя: {user.username}")
    elif len(new_name) < 3:
        answer = LEXICON['/change_name_error']
        await message.answer(answer, parse_mode='Markdown')
        await message.answer(text=f"Ваше текущее имя: {user.username}")
    else:
        game_service.user_repo.update_name(str(message.from_user.id), new_name)
        answer = LEXICON['/change_name_success'] + new_name
        await message.answer(answer, parse_mode='Markdown')


@router.message(Command(commands='new'))
async def new_game(message: Message):
    answer = game_service.create_game(str(message.from_user.id))
    await message.answer(answer, parse_mode='Markdown')

@router.message(Command(commands='join'))
async def join_game_command(message: Message):
    game_id = message.text[len('/join '):]  # The format is /join <game_id>
    if not game_id:
        answer = 'Error: you have not entered game ID'
    else:
        answer = game_service.join_game(str(message.from_user.id), game_id)
        admin = game_service.get_admin(game_id)
        from data.communication import send_to_player
        await send_to_player(admin, answer)

    await message.answer(answer)
    if answer == "success":
        pass  # to inform admin that user joined? maybe do it when game state is updated?


@router.message(lambda message: True)
async def unknown_command(message: Message):
    await message.answer('Unexpected message, I do nothing.\nPress /help to see available commands')
