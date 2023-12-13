#  game_setup_handlers
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from core.gameplay import Table
from lexicon.lexicon import LEXICON_RU as LEXICON
from data import game_service
from aiogram.filters import BaseFilter

# create_new_game, join_game, leave_game, kick_player, cancel_game, \
#    get_game_id_for_user, is_admin, set_cards, get_participants, get_name

# Инициализируем роутер уровня модуля
router = Router()
class CreatedFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool or int:
        user_id = str(message.from_user.id)
        user = game_service.user_repo.get_user(user_id)
        if user is None or user.current_game_id is None or user.current_game_status != 'created':
            return False
        current_table = game_service.game_repo.load_table(user.current_game_id, user.current_game_status)
        return {'user_id': user_id, 'current_table': current_table}


router.message.filter(CreatedFilter())


# new and join command are handled in default handlers (because user not in created yet)


@router.message(Command(commands='leave'))
async def leave_game_command(message: Message):
    answer = game_service.leave_game(str(message.from_user.id))
    await message.answer(answer)


@router.message(Command(commands='kick'))
async def kick_player_command(message: Message):
    user_id_to_kick = message.text[len('/kick '):]
    if len(user_id_to_kick) < 3:
        await message.answer(f"Error: user ID was not provided")
    else:
        await message.answer(game_service.kick_player(str(message.from_user.id), user_id_to_kick))


@router.message(Command(commands='cancel'))
async def cancel_game_command(message: Message):
    answer = game_service.cancel_game(str(message.from_user.id))
    await message.answer(answer)


@router.message(Command(commands='set_cards'))
async def set_cards_command(message: Message):
    answer = game_service.set_cards(str(message.from_user.id),
                                    message.text[11:].split())  # The format is /set_cards card1 card2 card3 ...
    await message.answer(answer)


@router.message(Command(commands='show_joined'))
async def show_joined_command(message: Message):
    user_id = str(message.from_user.id)
    game_id = game_service.user_repo.get_game_id_for_user(user_id, 'created')
    answer = game_service.get_participants(game_id)
    await message.answer(answer)

@router.message(Command(commands='play'))
async def play_game(message: Message, user_id: str, current_table: Table):
    pass
