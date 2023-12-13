import random
import time
from collections import Counter
from unactual_files.communication.communication import send_to_player, send_all, get_from_player
from core.global_setup import ROLES_INCLUSION_ORDER, NIGHT_ACTIONS_ORDER, MIN_NUM_PLAYERS, MAX_NUM_PLAYERS, \
    NUM_CARDS_IN_CENTER, MAX_NUM_ROUNDS, AWARDS
from dataclasses import dataclass, field
from core.actions import Actions
from enum import Enum

roles_inclusion_order = ROLES_INCLUSION_ORDER
night_actions_order = NIGHT_ACTIONS_ORDER
num_cards_in_center = NUM_CARDS_IN_CENTER
min_num_players = MIN_NUM_PLAYERS
max_num_players = MAX_NUM_PLAYERS
awards = AWARDS
format_dict = {}


@dataclass
class Table:
    # general
    game_id: str
    admin_id: str
    status: str

    # to start a game
    cards_set: list[str]
    roles_night_order: list[str]
    awards: Enum  # dict with points for victory
    players: list[str]  # list of players IDs: str
    # players_names: list[int]  # list of players usernames

    # for night actions
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

    def __post_init__(self):
        self.testing: bool = True
        self.cards = list(self.cards_set)
        self.num_players = len(self.cards) - NUM_CARDS_IN_CENTER
        self.num_center = NUM_CARDS_IN_CENTER
        random.shuffle(self.cards)
        self.roles = list(self.cards)
        self.actions = Actions(self)

        # Uncomment for debugging
        # self.cards = ['Приспешник', 'Камикадзе', 'Воришка', 'Жаворонок', 'Провидец', 'Вервульф', 'Вервульф', 'Шериф']

    def id_from_position(self, player_position: int) -> str:
        return self.players[player_position]

    # stages:
    def night_actions(self):
        for role in self.roles_night_order:
            send_all(self.num_players, f"Turn of {role}")
            for i, player in enumerate(self.roles[:-NUM_CARDS_IN_CENTER]):
                if player == role:
                    # Set the current player's position
                    self.performer_position = i
                    # Perform the action
                    self.actions.perform_action(role)
            if self.testing:
                print(self.cards)

    def discussion(self):
        t = len(self.cards[:-NUM_CARDS_IN_CENTER])

        send_all(self.num_players, f"It is time for discussion, you have {t + 2} minutes")
        if self.testing:
            time.sleep(3)  # lower time for testing
        else:
            time.sleep(t * 60)  # wait n+2 minutes
        send_all(self.num_players, f"You have 2 minutes left. After time is over you must stop talking.")
        if self.testing:
            time.sleep(2)  # lower time for testing
        else:
            time.sleep(2 * 60)  # wait 2 minutes
        send_all(self.num_players, f"Time is up, now close your eyes and vote")
        if self.testing:
            time.sleep(1)  # lower time for testing
        else:
            time.sleep(10)  # wait 10 seconds before voting

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
            # If there's a tie, use the priority order
            priority_order = ['blue', 'red', 'green', 'peaceful day']
            self.executed = min(max_voted, key=lambda card: priority_order.index(self.teams[card]))
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


def get_game_setup(admin=None, players_joined=None):
    if players_joined is not None and MIN_NUM_PLAYERS <= players_joined <= MAX_NUM_PLAYERS:
        num_players = players_joined
    else:
        while True:
            try:
                num_players = int(get_from_player(admin, "Enter the number of players: "))
                if num_players < MIN_NUM_PLAYERS or num_players > MAX_NUM_PLAYERS:
                    send_to_player(admin,
                                   f"Invalid number of players. Please enter a number between {MIN_NUM_PLAYERS} and {MAX_NUM_PLAYERS}.")
                    continue
                break
            except ValueError:
                send_to_player(admin, "Invalid input. Please enter integers only.")

    while True:
        try:
            num_rounds = int(get_from_player(admin, "Enter the number of rounds: "))
            if num_rounds < 1 or num_rounds > MAX_NUM_ROUNDS:
                send_to_player(admin,
                               f"Invalid number of rounds. Please enter a number between 1 and {MAX_NUM_ROUNDS}.")
                continue
            break
        except ValueError:
            send_to_player(admin, "Invalid input. Please enter integers only.")

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


def get_given_cards_set(admin=None):
    while True:
        setup_choice = get_from_player(admin, "Do you want to set up cards set manually? (yes/no): ").strip().lower()
        if setup_choice not in ['yes', 'no']:
            send_to_player(admin, "Invalid choice. Please enter 'yes' or 'no'.")
            continue
        if setup_choice == 'no':
            return []

        card_names_str = get_from_player(admin, "Enter the card names separated by spaces: ").strip()
        given_cards_set = [card.capitalize() for card in card_names_str.split(" ")]

        # Validate card names
        is_valid_set = True  # Set the flag to False
        cards_available = ROLES_INCLUSION_ORDER.copy()
        for card in given_cards_set:
            if card in cards_available:
                cards_available.remove(card)
            else:
                if card in ROLES_INCLUSION_ORDER:
                    send_to_player(admin,
                                   f"Exceeded the allowed number of {card} cards. Please enter a valid set of cards.")

                else:
                    send_to_player(admin, f"{card} is an invalid card name. Please enter only valid card names.")
                is_valid_set = False  # Set the flag to False

        if not is_valid_set:
            continue  # Continue the while loop if the set is not valid

        # Validate total number of cards (currently never used)
        total_cards = len(given_cards_set)
        if total_cards > MAX_NUM_PLAYERS + NUM_CARDS_IN_CENTER:
            send_to_player(admin,
                           f"Too many cards. The total number of cards should not exceed {MAX_NUM_PLAYERS + NUM_CARDS_IN_CENTER}.")
            continue

        return given_cards_set


def get_vote(player, num_players):
    max_attempts = 3
    attempts = 0  # Counter for the number of attempts
    while True:
        if attempts >= max_attempts:
            send_to_player(player, "Too many invalid attempts. Your vote will be considered as peaceful day.")
            return -1  # Or handle this case as you see fit

        try:
            vote_str = get_from_player(player, "Enter your vote: ").strip()  # Remove leading and trailing spaces
            vote = int(vote_str)

            if -1 <= vote <= num_players:
                return vote  # Exit the loop and return the vote
            else:
                send_to_player(player, f"Invalid vote. Please enter a number between -1 and {num_players}.")
                attempts += 1  # Increment the attempts counter

        except ValueError:
            send_to_player(player, "Invalid input. Please enter integers only.")
            attempts += 1  # Increment the attempts counter


def prepare_to_play(admin, players_joined):
    # game setup
    # can set admin and players_joined here
    num_players, num_rounds = get_game_setup(admin, players_joined)
    given_cards_set = get_given_cards_set(admin)
    cards_set = complete_cards_set(given_cards_set[:num_players + num_cards_in_center], num_players)
    return num_players, num_rounds, cards_set


def round(cards_set, roles_night_order):
    table = Table(cards_set, roles_night_order)  # shuffling and dealing cards
    send_all(table.num_players, f"The set of cards for this round is: {cards_set}")
    # for debugging
    for player, card in enumerate(table.cards[:table.num_players]):
        send_to_player(player, f"Your position is {player}, your card is {card}")  # players know their cards
    table.night_actions()
    table.discussion()
    table.get_teams()
    votes = []
    for player in range(table.num_players):
        votes.append(get_vote(player, table.num_players))
    # votes_string = get_from_player("All", "Enter votes separated with spaces: ")
    # votes = [int(vote) for vote in votes_string.split(" ")]
    table.voting(votes)
    table.get_scores_list()
    send_all(table.num_players, f"The final position is {table.cards}, the executed player is {table.executed}")
    send_all(table.num_players,
             f"The winning team is {table.winner_team}. The scores of this round are {table.scores}")
    return table.scores


def play():
    #  preparation
    admin = None
    players_joined = None
    num_players, num_rounds, cards_set = prepare_to_play(admin, players_joined)
    # cards_set = ['Баламут', 'Жаворонок', 'Камикадзе', 'Тигар', 'Ревизор', 'Шериф', 'Пьяница', 'Шаман', 'Интриган',
    #              'Стражник', 'Тигар', 'Вервульф', 'Вожак', 'Вервульф', 'Провидец', 'Приспешник', 'Воришка',
    #              'Двойник', 'Вервульф', 'Тигар']
    # cards_set = ['Двойник', 'Жаворонок', 'Тигар', 'Вервульф', 'Приспешник', 'Камикадзе', 'Тигар', 'Тигар']

    # еще для тестов можно не перемешивать карты в Table
    cards_set = ['Приспешник', 'Камикадзе', 'Воришка', 'Жаворонок', 'Провидец', 'Вервульф', 'Вервульф', 'Шериф']

    roles_night_order = get_night_order(cards_set)
    scores = [0] * num_players
    send_all(num_players, f"We are starting a game with {num_players} players and will play {num_rounds} round(-s).")
    # for player in range(num_players): send_to_player(player, f"Your position is: {player}. The deck: {cards_set}")
    # cycle for rounds
    for round_id in range(num_rounds):
        round_scores = round(cards_set, roles_night_order)  # running a single round
        # send_to_player('All', f"The scores of round {round_id} are {round_scores}.")
        for player in range(num_players):
            scores[player] += round_scores[player]
    for player in range(num_players):
        if scores[player] != 0:
            send_to_player(player, f"You got {scores[player]} point(-s) for victory")
        else:
            send_to_player(player, f"You lose in this round and receive no points")
    send_all(num_players, f"The final scores are: {scores}")
    send_all(num_players, f"The winner got {max(scores)} points")
