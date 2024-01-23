import random
import asyncio
import time
from collections import Counter
from dataclasses import dataclass, field

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# from enum import Enum

# from core.actions import Actions
from data.communication import send_to_player, send_multiple, get_from_player
from core.global_setup import ROLES_INCLUSION_ORDER, NIGHT_ACTIONS_ORDER, MIN_NUM_PLAYERS, MAX_NUM_PLAYERS, \
    NUM_CARDS_IN_CENTER, MAX_NUM_ROUNDS, AWARDS
from lexicon.lexicon import action_description_ru



roles_inclusion_order = ROLES_INCLUSION_ORDER
night_actions_order = NIGHT_ACTIONS_ORDER
num_cards_in_center = NUM_CARDS_IN_CENTER
min_num_players = MIN_NUM_PLAYERS
max_num_players = MAX_NUM_PLAYERS
awards = AWARDS
format_dict = {}

action_description = action_description_ru
def translate_en_ru(key: str) -> str:
    dictionary = {
        'red': 'красная',
        'green': 'зеленая',
        'blue': 'голубая'
    }
    return dictionary[key]


@dataclass
class Table:
    # general
    game_id: str
    admin_id: str
    status: str

    # to start a game

    roles_night_order: list[str]
    awards: dict  # dict with points for victory
    players: list[str]  # list of players IDs: str
    nicknames: list[int]  # list of players usernames

    cards_set: list[str] = field(default_factory=list)

    # for night actions
    actions: any = None  # import will be done in night actions module
    next_role: str | None = None  # "Werewolf" or "Voting"
    performer_position: int | None = None  # to keep track of the performing player
    guarded_card: int | None = None  # card blocked from actions index
    doppelganger_role: int | None = None
    doppelganger_wakeup_count: int = 0
    doppelganger_positions: int | None = None  # in case he is inspector or intriguer
    inspector_positions: int | None = None
    intriguer_positions: int | None = None

    # for determining winners
    teams: list[str] = field(default_factory=list)
    executed: int | None = None
    winner_team: str = 'error_no_winners'
    scores: list[int] = field(default_factory=list)  # Correct: each instance will get a new list

    def __post_init__(self):  # runned when creating a table, not when starting a game?
        self.testing: bool = False
        self.cards = list(self.cards_set)
        self.num_players = len(self.players) - NUM_CARDS_IN_CENTER
        self.num_center = NUM_CARDS_IN_CENTER
        random.shuffle(self.cards)  # why shuffle here?
        self.roles = list(self.cards)

        # Uncomment for debugging
        # self.cards = ['Приспешник', 'Камикадзе', 'Воришка', 'Жаворонок', 'Провидец', 'Вервульф', 'Вервульф', 'Шериф']

    def id_from_position(self, player_position: int) -> str:
        return self.players[player_position]

    # stages:
    async def night_actions(self):
        from core.actions import Actions
        self.actions = Actions(self)
        for role in self.roles_night_order:
            await send_multiple(self.players, f"__Ходит {role}.__\n{action_description[role]}")

            # List to hold player actions for the current role
            current_role_actions = []

            for i, player in enumerate(self.roles[:-NUM_CARDS_IN_CENTER]):
                if player == role:
                    self.performer_position = i
                    self.next_role = role
                    from data import game_service
                    game_service.game_repo.save_game_state(self.game_id, self, self.status)

                    # Add the player's action to the list
                    current_role_actions.append(self.actions.perform_action(role))

            # Define the random delay
            random_delay = 1 if self.testing else random.triangular(5, 30, 10)

            # If there are player actions, run them concurrently with the delay
            if current_role_actions:
                await asyncio.gather(
                    *current_role_actions,
                    asyncio.sleep(random_delay)
                )
            else:
                # If there are no player actions, just run the delay
                await asyncio.sleep(random_delay)

            if self.testing:
                print(self.cards)

    async def discussion(self):
        t = len(self.cards[:-NUM_CARDS_IN_CENTER])
        self.testing = True
        await send_multiple(self.players, f"Пришло время для обсуждения, у вас {t + 2} минут.")
        if self.testing:
            await asyncio.sleep(3)  # lower time for testing
        else:
            await asyncio.sleep(t * 60)  # wait n+2 minutes
        await send_multiple(self.players, f"Осталось 2 минуты.")
        if self.testing:
            await asyncio.sleep(2)  # lower time for testing
        else:
            await asyncio.sleep(2 * 60)  # wait 2 minutes
        await send_multiple(self.players, f"Время вышло, обсуждать больше ничего нельзя!")
        if self.testing:
            await asyncio.sleep(1)  # lower time for testing
        else:
            await asyncio.sleep(10)  # wait 10 seconds before voting
        self.testing = False


    """
    async def discussion(self):
        t = len(self.cards[:-NUM_CARDS_IN_CENTER])
        await send_multiple(self.players, f"Пришло время для обсуждения, у вас {t + 2} минут.")

        # Create tasks for discussion timers
        self.discussion_tasks = [
            asyncio.create_task(asyncio.sleep(3 if self.testing else t * 60)),
            asyncio.create_task(asyncio.sleep(2 if self.testing else 2 * 60)),
            asyncio.create_task(asyncio.sleep(1 if self.testing else 5))
        ]
        try:
            # Wait for the first timer (discussion period)
            await self.discussion_tasks[0]
            await send_multiple(self.players, f"Осталось 2 минуты.")
            # Wait for the second timer (final 2 minutes)
            await self.discussion_tasks[1]
            await send_multiple(self.players, f"Время вышло, обсуждать больше ничего нельзя!")
        except asyncio.CancelledError:
            # If timers are cancelled, move directly to voting
            await send_multiple(self.players, f"Переходим к досрочному голосованию.")
        # Wait for the third timer (before voting)
        await self.discussion_tasks[2]


    async def skip_discussion(self):
        for task in self.discussion_tasks:
            task.cancel()
        # Clear the tasks list after canceling to avoid potential issues
        self.discussion_tasks.clear()
"""

    def get_teams(self):
        for player in self.cards[:self.num_players]:
            if player == 'Двойник':
                player = self.doppelganger_role  # substitute doppelganger with his actual card
            if player == 'Камикадзе':
                self.teams.append('blue')
            elif player in ['Вожак', 'Вервульф', 'Приспешник']:
                self.teams.append('red')
            else:
                self.teams.append('green')

    def voting(self, votes):
        # Count the votes
        vote_counts = Counter(votes)
        max_votes = max(vote_counts.values())
        # Get the players with the most votes
        max_voted = [player for player, count in vote_counts.items() if count == max_votes]
        # for purposes of determining a winner his color must be green
        self.teams = ['green' if role == 'Приспешник' else team for role, team in
                      zip(self.cards[:self.num_players], self.teams)]
        # Determine the executed player
        if len(max_voted) > 1:
            # Filter out the 'peaceful day' vote (-1), because it never beats the other winner
            max_voted = [vote for vote in max_voted if vote != -1]
            # If there's a tie, use the priority order
            priority_order = ['blue', 'red', 'green']
            self.executed = min(max_voted, key=lambda position: priority_order.index(self.teams[position]))
        else:
            self.executed = max_voted[0]

        if self.executed != -1:  # if NOT peaceful day
            executed_team = self.teams[self.executed]
            if executed_team == 'blue':
                self.winner_team = 'blue'
            elif executed_team == 'red':
                self.winner_team = 'green'
            elif executed_team == 'green':
                self.winner_team = 'red'
        else:  # if peaceful day
            if any(team == 'red' for team in self.teams):
                self.winner_team = 'red'
            else:
                self.winner_team = 'green'
        # changing color back for correct scoring
        self.teams = ['red' if role == 'Приспешник' else team for role, team in
                      zip(self.cards[:self.num_players], self.teams)]

    def get_scores_list(self):
        # Determine the score for each player

        for player in self.teams:
            if player == self.winner_team:
                self.scores.append(self.awards[self.winner_team])
            else:
                self.scores.append(0)


async def get_game_setup(admin=None, players_joined=None):
    if players_joined is not None and MIN_NUM_PLAYERS <= players_joined <= MAX_NUM_PLAYERS:
        num_players = players_joined
    else:
        while True:
            try:
                num_players = int(await get_from_player(admin, "Enter the number of players: "))
                if num_players < MIN_NUM_PLAYERS or num_players > MAX_NUM_PLAYERS:
                    await send_to_player(admin,
                                         f"Invalid number of players. Please enter a number between {MIN_NUM_PLAYERS} and {MAX_NUM_PLAYERS}.")
                    continue
                break
            except ValueError:
                await send_to_player(admin, "Invalid input. Please enter integers only.")

    while True:
        try:
            num_rounds = int(await get_from_player(admin, "Enter the number of rounds: "))
            if num_rounds < 1 or num_rounds > MAX_NUM_ROUNDS:
                await send_to_player(admin,
                                     f"Invalid number of rounds. Please enter a number between 1 and {MAX_NUM_ROUNDS}.")
                continue
            break
        except ValueError:
            await send_to_player(admin, "Invalid input. Please enter integers only.")

    return num_players, num_rounds


def complete_cards_set(given_cards_set, num_players):
    cards_set = given_cards_set.copy()

    for role in roles_inclusion_order:
        if role in given_cards_set:
            given_cards_set.remove(role)  # removing from the original list to exclude double-counting
        else:
            cards_set.append(role)
        if len(cards_set) == num_players + num_cards_in_center:
            if cards_set.count('Тигар') != 1:  # Should be none or at least 2 of them
                break
            else:
                cards_set.remove('Тигар')
    return cards_set


def get_night_order(cards_set):
    roles_night_order = []

    for action in night_actions_order:
        if action in cards_set:
            roles_night_order.append(action)  # if double action, should be parsed while doing so
            if action == 'Вожак' and 'Вервульф' not in cards_set:
                roles_night_order.append('Вервульф')  # if only Вожак we should have werewolf stage anyway
    return roles_night_order


# communication functions


async def get_given_cards_set(admin=None):
    while True:
        setup_choice = await get_from_player(admin,
                                             "Do you want to set up cards set manually? (yes/no): ")
        if setup_choice.strip().lower() not in ['yes', 'no']:
            await send_to_player(admin, "Invalid choice. Please enter 'yes' or 'no'.")
            continue
        if setup_choice == 'no':
            return []

        card_names_str = await get_from_player(admin, "Enter the card names separated by spaces: ")
        card_names_str.strip()
        given_cards_set = [card.capitalize() for card in card_names_str.split()]

        # Validate card names
        is_valid_set = True  # Set the flag to False
        cards_available = ROLES_INCLUSION_ORDER.copy()
        for card in given_cards_set:
            if card in cards_available:
                cards_available.remove(card)
            else:
                if card in ROLES_INCLUSION_ORDER:
                    await send_to_player(admin,
                                         f"Exceeded the allowed number of {card} cards. Please enter a valid set of cards.")

                else:
                    await send_to_player(admin, f"{card} is an invalid card name. Please enter only valid card names.")
                is_valid_set = False  # Set the flag to False

        if not is_valid_set:
            continue  # Continue the while loop if the set is not valid

        # Validate total number of cards (currently never used)
        total_cards = len(given_cards_set)
        if total_cards > MAX_NUM_PLAYERS + NUM_CARDS_IN_CENTER:
            await send_to_player(admin,
                                 f"Too many cards. The total number of cards should not exceed {MAX_NUM_PLAYERS + NUM_CARDS_IN_CENTER}.")
            continue

        return given_cards_set


async def get_vote(player, num_players, keyboard=None):
    max_attempts = 3
    attempts = 0  # Counter for the number of attempts
    while True:
        if attempts >= max_attempts:
            await send_to_player(player, "Too many invalid attempts. Your vote will be considered as peaceful day.")
            return -1  # Or handle this case as you see fit

        try:
            vote_list: list = await get_from_player(player, "Проголосуйте за одного из участников или за мирный день:", keyboard)
            vote = int(vote_list[0])  # get from player return list

            if -1 <= vote < num_players:
                return vote  # Exit the loop and return the vote
            else:  # we never get here because of check in handler
                await send_to_player(player, f"Invalid vote. Please enter a number between -1 and {num_players - 1}.")
                attempts += 1  # Increment the attempts counter

        except ValueError:
            await send_to_player(player, "Invalid input. Please enter integers only.")
            attempts += 1  # Increment the attempts counter


async def prepare_to_play(admin, players_joined):
    # game setup
    # can set admin and players_joined here
    num_players, num_rounds = await get_game_setup(admin, players_joined)
    given_cards_set = await get_given_cards_set(admin)
    cards_set = complete_cards_set(given_cards_set[:num_players + num_cards_in_center], num_players)
    return num_players, num_rounds, cards_set


async def play_round(table):
    cards_set, roles_night_order = table.cards_set, table.roles_night_order
    table.cards = table.cards_set

    # shuffle the cards HERE
    random.shuffle(table.cards)

    table.roles = table.cards.copy()

    await send_multiple(table.players,
                        f"В игре участвуют: {', '.join(table.nicknames)}.\n"
                        f"Набор кард в этом раунде: {', '.join(cards_set)}\n"
                        f"Порядок ночных действий: {', '.join(roles_night_order)}")
    for player_id, card in zip(table.players, table.cards[:table.num_players]):
        await send_to_player(player_id, f"Ваша карта: {card}\n{action_description[card]}")  # players know their cards
    await table.night_actions()
    await table.discussion()
    table.get_teams()
    votes = []
    # print(table.next_role)
    table.next_role = 'Voting'
    from data import game_service
    game_service.game_repo.save_game_state(table.game_id, table, table.status)
    keyboard = generate_voting_keyboard(table)
    # Now modify the loop like this:
    vote_tasks = []
    import asyncio
    for player in table.players:
        # Start the get_vote as a task, so it doesn't wait for others to finish
        task = asyncio.create_task(get_vote(player, table.num_players, keyboard))
        vote_tasks.append(task)

    # Now you need to await the tasks and collect the votes
    votes = await asyncio.gather(*vote_tasks)
    # votes = [int(vote) for vote in votes_string.split(" ")]
    table.voting(votes)
    table.get_scores_list()
    game_service.game_repo.save_game_state(table.game_id, table, table.status)
    game_service.game_repo.move_table(table.game_id, 'started', 'completed')
    for player_id in table.players:
        game_service.user_repo.update_game_id_and_status_for_user(player_id, None, None)

    final_position = ', '.join([f'{name}: {card}' for name, card in zip(table.nicknames, table.cards[:-table.num_center])])
    executed = 'мирный день' if table.executed == -1 else table.nicknames[table.executed]
    await send_multiple(table.players,
                        f"Итоговый расклад:\n{final_position}\nБольше всего голосов набрал {executed}\n"
                        f"Победила {translate_en_ru(table.winner_team)} команда.")
    return table.scores


async def play(current_table: Table):
    #  preparation
    # cards_set = ['Баламут', 'Жаворонок', 'Камикадзе', 'Тигар', 'Ревизор', 'Шериф', 'Пьяница', 'Шаман', 'Интриган',
    #              'Стражник', 'Тигар', 'Вервульф', 'Вожак', 'Вервульф', 'Провидец', 'Приспешник', 'Воришка',
    #              'Двойник', 'Вервульф', 'Тигар']
    # cards_set = ['Двойник', 'Жаворонок', 'Тигар', 'Вервульф', 'Приспешник', 'Камикадзе', 'Тигар', 'Тигар']
    # ДЛЯ ТЕСТОВ можно не перемешивать карты в Table

    current_table.num_players = len(current_table.players)

    if current_table.testing:
        current_table.cards_set = ['Провидец', 'Воришка', 'Шериф', 'Пьяница', 'Вервульф']  # , 'Вервульф', 'Вервульф', 'Шериф']
    else:
        current_table.cards_set = complete_cards_set(current_table.cards_set, current_table.num_players)

    current_table.roles_night_order = get_night_order(current_table.cards_set)
    scores = [0] * current_table.num_players
    # await send_multiple(current_table.players,
    #                     f"Вы начинаете игру с {current_table.num_players} участниками: {current_table.nicknames}")  # and will play {num_rounds} round(-s).")

    # cycle for rounds
    for round_id in range(1):  # NO functionality for multy-rounds now
        current_table.status = 'started'

        round_scores = await play_round(current_table)  # running a single play_round

        # await send_to_player('All', f"The scores of play_round {round_id} are {round_scores}.")
        for player in range(current_table.num_players):
            scores[player] += round_scores[player]
    for player in range(current_table.num_players):
        if scores[player] != 0:
            await send_to_player(current_table.players[player], f"Вы получаете {scores[player]} балл за победу.")
        else:
            await send_to_player(current_table.players[player], f"В этом раунде вы проиграли и не получаете очков.")
    # await send_multiple(current_table.players, f"The final scores are: {scores}")
    # await send_multiple(current_table.players, f"The winner got {max(scores)} points")


def generate_voting_keyboard(table) -> InlineKeyboardMarkup:
    # Add player buttons
    player_buttons = []
    for position, nickname in zip(range(len(table.nicknames)), table.nicknames):
        # Using player_id as callback data, modify as needed
        button = InlineKeyboardButton(text=str(nickname), callback_data=str(position))
        player_buttons.append(button)

    # Add peaceful day option
    peaceful_day_button = [InlineKeyboardButton(text=f"Мирный день", callback_data=str(-1))]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[player_buttons, peaceful_day_button])
    return keyboard


'''
# Usage example
table = Table(
    game_id="123",
    admin_id="admin",
    status="active",
    roles_night_order=["role1", "role2"],
    awards={"win": 10},
    players=["player1", "player2", "player3"],
    nicknames=["User1", "User2", "User3"]
)
keyboard = generate_table_keyboard(table)
'''
