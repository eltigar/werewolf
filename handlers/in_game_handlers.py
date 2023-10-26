from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU as LEXICON

# Инициализируем роутер уровня модуля
router = Router()

'''
# Example in-game command handler
@router.message(Command('abort'))
async def play_game(message: Message):
    # in-game logic here
    pass

# ... Add other in-game handlers here
'''