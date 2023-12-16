from enum import Enum

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from data import game_service
from core.gameplay import Table
from aiogram.filters import BaseFilter
from data import communication

# Инициализируем роутер уровня модуля
router = Router()


class StartedFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict:
        user_id = str(message.from_user.id)
        user = game_service.user_repo.get_user(user_id)
        if user is None or user.current_game_id is None or user.current_game_status != 'started':
            return False
        current_table = game_service.game_repo.load_table(user.current_game_id, user.current_game_status)
        return {'user_id': user_id, 'current_table': current_table}


router.message.filter(StartedFilter())


class Positions(Enum):
    center = [-3, -2, -1]
    player = [1, 2, 3, 4, 5, 6]


class PromptFormat(Enum):  # проблема в том что в игре имя роли хранится как строка на русском языке
    doppelganger = ['player']
    guard = ['any']
    alpha = ['player']
    werewolf = ['center']  # only if alone
    minion = None
    tigar = None
    seer = ['center', 'center']
    sheriff = ['player']
    inspector = ['player']
    intriguer = ['player', 'player']
    robber = ['player']
    troublemaker = ['player', 'player']
    shaman = ['player', 'center']
    drunk = ['center']
    morninger = None
    suicidal = None




def validate_input(role: str, action_args: list[int], performer_position: int, guarded_card: int,
                   num_players: int, cards_in_center: int) -> str:
    input_format = PromptFormat[role].value
    # Get the input from the user
    # Check if the input matches the format
    answer: str = 'Input seems valid'
    if len(action_args) != len(input_format):
        answer = "Invalid number of arguments. Please try again."
    else:  # Check if the input is valid
        for i, arg in enumerate(action_args):  # do checks for each entered argument
            if not isinstance(arg, int):  # checks for being integer
                answer = "Invalid input type. Please enter an integer."
            elif performer_position == arg:
                answer = "You cannot act on your own card. Please try again."
            elif guarded_card == arg:
                answer = "The card you entered is blocked. Please try again."
            elif i == 1 and action_args[0] == action_args[1]:
                answer = "You cannot act on the same card twice. Please try again."
            elif input_format[i] == 'player':
                if not (0 <= arg < num_players):
                    answer = "Invalid player position. Please try again."
            elif input_format[i] == 'center':
                if not (-cards_in_center <= arg < 0):
                    answer = "Invalid center position. Please try again."
            elif input_format[i] == 'any':
                if not (0 <= arg < num_players + cards_in_center):
                    answer = "Invalid card position. Please try again."
    return answer


@router.message(Command('abort'))
async def abort_game(message: Message, user_id: str, current_table: Table):
    if user_id == current_table.admin_id:
        answer = game_service.abort_game(current_table.game_id)
        await message.answer(answer)  # должно отправляться всем
    else:
        await message.answer("Not admin of the game")


@router.message()
async def process_in_game_command(message: Message, user_id: str, current_table: Table) -> str or None:
    if current_table.next_role is None:
        await message.answer("It's nobody's turn now")
    elif current_table.next_role == 'Voting':
        if -1 <= int(message.text) <= current_table.num_players:
            communication.set_player_input(user_id, list(map(int, message.text.split())))
        else:
            await message.answer(f"Incorrect vote.\nPlease enter a number between -1 and {current_table.num_players}")
        # calls function in game service, not needed
        # await message.answer(game_service.accept_vote(current_table.game_id, user_id, message.text))
    elif current_table.performer_position != current_table.players.index(user_id):  # whether this is a turn of a player
        await message.answer("It's not your turn now")
    else:
        action_args: list[int] = list(map(int, message.text.split()))
        answer: str = 'Input seems valid'
        #    validate_input(current_table.next_role, action_args,
        #                             current_table.performer_position, current_table.guarded_card,
        #                             current_table.num_players, current_table.num_center)
        if answer != 'Input seems valid':
            await message.answer("Incorrect format of data. Should be {pformat.next_role}.")
        else:
            communication.set_player_input(user_id, action_args)


'''
        # Check if awaiting a specific player
        if game_state == user_id:
            return True
        # Check if awaiting voting and user is a participant
        elif game_state == -1:
            return True
        # If the player is in game but not the one awaited
        else:
            
            return False

class SpecificPlayerAwaitingFilter(BaseFilter):
    key = 'awaiting_player_id'

    async def __call__(self, message: Message, awaiting_player_id: str) -> bool:
        user_id = message.from_user.id

        if game.awaiting_for == user_id:

        game_id = get_game_id_for_user(user_id)
        if game_id is None:
            return False  # User is not in a game

        game_state = get_game_state(game_id)
        return str(user_id) == awaiting_player_id


class VotingAwaitingFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        game_id = get_game_id_for_user(user_id)
        if game_id is None:
            return False  # User is not in a game

        game_state = get_game_state(game_id)
        return game_state == "voting" and is_user_part_of_game(user_id, game_id)


class NotAwaitedPlayerFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        game_id = get_game_id_for_user(user_id)
        if game_id is None:
            return False  # User is not in a game

        game_state = get_game_state(game_id)
        if game_state != str(user_id) and game_state != "voting":
            await message.answer("It's not your turn now")
            return False
        return True


# Bind the filter to the router
router.message.bind_filter(AwaitingForFilter())


@router.message(AwaitingForFilter())
async def game_message_handler(message: Message):
    # Pass the message to the game logic for processing
    response = await process_game_message(message.from_user.id, message.text)
    await message.answer(response)


# Example in-game command handler


# ... Add other in-game handlers here
'''
