import asyncio
import random
from collections import Counter
from dataclasses import dataclass, field

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.global_setup import ROLES_INCLUSION_ORDER, NIGHT_ACTIONS_ORDER, MIN_NUM_PLAYERS, MAX_NUM_PLAYERS, \
    NUM_CARDS_IN_CENTER, MAX_NUM_ROUNDS, AWARDS
from core.roles_info import represent_cards_set, ROLES_DICT
# from core.actions import Actions
from data.communication import send_to_player, send_multiple, get_from_player
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
    nicknames: list[str]  # list of players usernames

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
    scores: list[int] = field(default_factory=list)
    accumulated_scores: dict[str, int] = field(default_factory=dict)
    discussion_cancel_event: None | asyncio.Event = None

    def __post_init__(self):  # run when creating a table, not when starting a game?
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
            if role == 'Двойник' and self.doppelganger_role is not None:
                text = f"Ходит {str(ROLES_DICT[role])}.\nЕсли Двойник стал Ревизором, Интриганом, Пьяницей, Жаворонком, то он просыпается и выполняет свое второе/предутреннее действие."
            else:
                text = f"Ходит {str(ROLES_DICT[role])}.\n{ROLES_DICT[role].description}"
            await send_multiple(self.players, text)

            # Coroutines for role actions amd random delay
            async def role_actions_coroutine():
                for i, player in enumerate(self.roles[:-NUM_CARDS_IN_CENTER]):
                    if player == role:
                        self.performer_position = i
                        self.next_role = role
                        from data import game_service
                        game_service.game_repo.save_game_state(self.game_id, self, self.status)
                        await self.actions.perform_action(role)

            async def random_delay_coroutine():
                delay = 1 if self.testing else random.triangular(5, 30, 10)
                await asyncio.sleep(delay)

            # Run role actions and random delay concurrently
            await asyncio.gather(
                role_actions_coroutine(),
                random_delay_coroutine()
            )
            if self.testing:
                print(self.cards)

    async def discussion(self):  # temp version with ability to vote early
        t = len(self.cards[:-NUM_CARDS_IN_CENTER])
        testing_state = self.testing
        self.testing = True  # function is a placeholder
        await send_multiple(self.players, f"Пришло время для обсуждения, у вас {t + 2} минут.")
        if self.testing:
            await asyncio.sleep(2)  # lower time for testing
            await send_multiple(self.players, f"Пожалуйста, засеките время самостоятельно.")
        else:
            await asyncio.sleep(t * 60)  # wait n minutes
            await send_multiple(self.players, f"Осталось 2 минуты.")
            await asyncio.sleep(2 * 60)  # wait 2 minutes
            await send_multiple(self.players, f"Время вышло, обсуждать больше ничего нельзя!")

        self.testing = testing_state

        if self.testing:
            await asyncio.sleep(5)  # lower time for testing
        else:
            await asyncio.sleep(30)  # wait 10 seconds before voting




    async def discussion_timer(self, delay):
        try:
            await asyncio.wait_for(self.discussion_cancel_event.wait(), timeout=delay)
        except asyncio.TimeoutError:
            pass  # Normal timeout, continue execution
        if self.discussion_cancel_event.is_set():
            raise asyncio.CancelledError

    async def discussion2(self):  # renamed to pick simple function
        t = len(self.cards[:-NUM_CARDS_IN_CENTER])
        await send_multiple(self.players, f"Пришло время для обсуждения, у вас {t + 2} минут.")

        self.discussion_cancel_event = asyncio.Event()

        try:
            await self.discussion_timer(10 if self.testing else t * 60)
            await send_multiple(self.players, "Осталось 2 минуты.")

            await self.discussion_timer(25 if self.testing else 2 * 60)
            await send_multiple(self.players, "Время вышло, обсуждать больше ничего нельзя!")

        except asyncio.CancelledError:
            print("Discussion was cancelled.")
            await send_multiple(self.players, "Переходим к досрочному голосованию.")
        finally:
            self.discussion_cancel_event = None  # Reset the event for the next discussion
            await asyncio.sleep(5 if self.testing else 5)

    async def skip_discussion(self):
        if self.discussion_cancel_event is not None:
            self.discussion_cancel_event.set()  # Signal to cancel the discussion
            return 'Discussion skipped'
        else:
            return "Error: unable to reach discussion Event"

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

    def generate_scores_with_medals(self):
        # Define the medals
        medals = ["🥇", "🥈", "🥉"]
        medals_left = medals.copy()
        medals_count = 0
        # Determine the unique score values
        sorted_scores = sorted(set(self.accumulated_scores.values()), reverse=True)
        medals_dict = {}
        for top_result in sorted_scores[:3]:
            for name, score in self.accumulated_scores.items():
                if score == top_result:
                    medals_dict[name] = medals_left[0]
                    medals_count += 1
            medals_left = medals[medals_count:]
            if not medals_left:
                break
        # Generate the scores text with medals
        scores_text = "\n".join(
            f"{name}: {score}{medals_dict.get(name, '')}" for name, score in self.accumulated_scores.items())
        return scores_text


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
        if len(cards_set) >= num_players + num_cards_in_center:
            cards_set = cards_set[:num_players + num_cards_in_center]
            if cards_set.count('Тигар') != 1:  # Should be none or at least 2 of them
                break
            else:
                cards_set.remove('Тигар')
            # just for testing
            if num_players == 2:
                cards_set.remove('Баламут') if 'Баламут' in cards_set else True
                cards_set.remove('Интриган') if 'Интриган' in cards_set else True

    return cards_set


def get_night_order(cards_set):
    roles_night_order = []
    # Determine if a second 'Двойник' is needed
    second_timeslot_doppel = any(item in cards_set for item in ["Интриган", "Ревизор", "Пьяница", "Жаворонок"])
    for role in night_actions_order:
        if role in cards_set:
            if role == 'Двойник' and 'Двойник' in roles_night_order:
                if second_timeslot_doppel:
                    roles_night_order.append(role)  # Add second 'Двойник' if conditions are met
                else:
                    pass  # no second adding for this case
            else:
                roles_night_order.append(role)  # Add other roles
                if role == 'Вожак' and 'Вервульф' not in cards_set:
                    roles_night_order.append('Вервульф')  # Special case for 'Вожак'

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


async def get_vote(player, num_players, keyboard=None) -> int:
    max_attempts = 3
    attempts = 0  # Counter for the number of attempts
    while True:
        if attempts >= max_attempts:
            await send_to_player(player, "Too many invalid attempts. Your vote will be considered as peaceful day.")
            return -1  # Or handle this case as you see fit

        try:
            vote_list: list = await get_from_player(player, "Проголосуйте за одного из участников или за мирный день:",
                                                    keyboard)
            vote = int(vote_list[0])  # get from player return list

            if -1 <= vote < num_players:
                return vote  # Exit the loop and return the vote
            else:  # we never get here because of check in handler
                await send_to_player(player, f"Invalid vote. Please enter a number between -1 and {num_players - 1}.")
                attempts += 1  # Increment the attempts counter

        except ValueError:
            await send_to_player(player, "Invalid input. Please enter integers only.")
            attempts += 1  # Increment the attempts counter


async def prepare_round(table: Table) -> None:  # admin, players_joined):
    # game setup
    table.cards = table.cards_set.copy()
    await send_multiple(table.players,
                        f"В игре участвуют: {', '.join(table.nicknames)}.\n" +
                        represent_cards_set(ROLES_DICT, table.cards_set))

    # shuffle the cards HERE
    if not table.testing:
        random.shuffle(table.cards)
    table.roles = table.cards.copy()

    for player_id, card in zip(table.players, table.cards[:table.num_players]):
        await send_to_player(player_id,
                             f"Ваша карта: {str(ROLES_DICT[card])}\n{ROLES_DICT[card].description}\nНочь начнется через 10 секунд.")  # players know their cards
    import asyncio
    if table.testing:
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(10)
    """
    # can set admin and players_joined here
    num_players, num_rounds = await get_game_setup(admin, players_joined)
    given_cards_set = await get_given_cards_set(admin)
    cards_set = complete_cards_set(given_cards_set[:num_players + num_cards_in_center], num_players)
    return num_players, num_rounds, cards_set
    """


async def play_round(table: Table) -> None:
    await send_multiple(table.players,
                        f"Начинается ночь! Постарайтесь сидеть в телефоне в течение всей ночи.")

    await table.night_actions()
    await send_multiple(table.players,
                        represent_cards_set(ROLES_DICT, table.cards_set))
    await table.discussion()
    table.get_teams()
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

    final_position = ', '.join(
        [f'{name}: {card}' for name, card in zip(table.nicknames, table.cards[:-table.num_center])])
    final_center = ', '.join(table.cards[-table.num_center:])
    executed = 'мирный день' if table.executed == -1 else table.nicknames[table.executed]
    await send_multiple(table.players,
                        f"Итоговый расклад:\n{final_position}\nЦентр: {final_center}\nБольше всего голосов набрал {executed}\n"
                        f"Победила {translate_en_ru(table.winner_team)} команда.")

    for player, nickname, score in zip(table.players, table.nicknames, table.scores):
        if score != 0:
            await send_to_player(player, f"Вы получаете {score} балл за победу.")
        else:
            await send_to_player(player, f"В этом раунде вы проиграли и не получаете очков.")
        table.accumulated_scores[nickname] = table.accumulated_scores.get(nickname, 0) + score
    scores_text = "The final scores are:\n" + table.generate_scores_with_medals()
    await send_multiple(table.players, scores_text)

    # saving the state
    game_service.game_repo.save_game_state(table.game_id, table, table.status)
    game_service.game_repo.move_table(table.game_id, 'started', 'completed')
    for player_id in table.players:
        game_service.user_repo.update_game_id_and_status_for_user(player_id, None, None)


async def play(current_table: Table) -> None:
    #  preparation
    current_table.num_players = len(current_table.players)
    if current_table.testing:
        current_table.cards_set = ['Двойник', 'Вервульф', 'Жаворонок', 'Камикадзе',
                                   'Вервульф']  # , 'Вервульф', 'Вервульф', 'Шериф']
    else:
        current_table.cards_set = complete_cards_set(current_table.cards_set, current_table.num_players)
    current_table.roles_night_order = get_night_order(current_table.cards_set)

    # playing
    current_table.status = 'started'
    await prepare_round(current_table)
    await play_round(current_table)

    await send_to_player(current_table.admin_id, f'If you want to continue, send `/repeat {current_table.game_id}`')


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
