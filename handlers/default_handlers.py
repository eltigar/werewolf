from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU as LEXICON
from data_storage.data import add_user, get_user, update_name

# Инициализируем роутер уровня модуля
router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON['/start'])
    # Если пользователь только запустил бота и его нет в словаре - добавляем его в словарь
    # функция внутри проверит, что его еще нет
    add_user(message.from_user.id, message.from_user.first_name)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON['/help'])


# Change name handler as you specified
@router.message(Command(commands='change_name'))
async def change_name_command(message: Message):
    # change name logic here
    new_name = message.text[13:]
    if len(new_name) == 0:
        await message.answer(text=LEXICON['/change_name_request'])
    elif len(new_name) < 3:
        await message.answer(text=LEXICON['/change_name_error'])
    else:
        update_name(message.from_user.id, new_name)
        await message.answer(text=LEXICON['/change_name_success'] + new_name)




# Handle all unspecified commands
@router.message(lambda message: True)
async def unknown_command(message: Message):
    await message.answer('Unexpected message, I do nothing.\nPress /help to see available commands')

# ... Add other default handlers here
