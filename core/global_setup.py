import json
import os
from enum import Enum


'''
class Awards(Enum):
    GREEN = 1
    RED = 1
    BLUE = 1
    
    
class CardNameRU(Enum):
    GUARD = "Стражник"
    DOPPELGANGER = "Двойник"
    ALPHA = "Вожак"
    WEREWOLF = "Вервульф"
    MINION = "Приспешник"
    TIGAR = "Тигар"
    SHERIFF = "Шериф"
    SEER = "Провидец"
    INSPECTOR = "Ревизор"
    INTRIGUER = "Интриган"
    ROBBER = "Воришка"
    TROUBLEMAKER = "Баламут"
    SHAMAN = "Шаман"
    DRUNK = "Пьяница"
    MORNINGER = "Жаворонок"
    SUICIDAL = "Камикадзе"


class CardNameEN(Enum):
    GUARD = "Guard"
    DOPPELGANGER = "Doppelganger"
    ALPHA = "Alpha"
    WEREWOLF = "Werewolf"
    MINION = "Minion"
    TIGAR = "Tigar"
    SHERIFF = "Sheriff"
    SEER = "Seer"
    INSPECTOR = "Inspector"
    INTRIGUER = "Intriguer"
    ROBBER = "Robber"
    TROUBLEMAKER = "Troublemaker"
    SHAMAN = "Shaman"
    DRUNK = "Drunk"
    MORNINGER = "Morninger"
    SUICIDAL = "Suicidal"


# Now you can create a list of roles for inclusion order using Enum members:
roles_inclusion_order = [
    Role.WEREWOLF, Role.SUICIDAL, Role.ROBBER, Role.TROUBLEMAKER,
    Role.MINION, Role.DOPPELGANGER, Role.SEER, Role.MORNINGER,
    Role.SHERIFF, Role.WEREWOLF, Role.TIGAR, Role.TIGAR, Role.SHAMAN,
    Role.INTRIGUER, Role.DRUNK, Role.INSPECTOR, Role.ALPHA, Role.GUARD,
    Role.TIGAR, Role.WEREWOLF
]

# And a list for the night actions order:
night_actions_order = [
    Role.DOPPELGANGER, Role.GUARD, Role.ALPHA, Role.WEREWOLF, Role.MINION,
    Role.TIGAR, Role.SEER, Role.SHERIFF, Role.INSPECTOR, Role.INTRIGUER,
    Role.ROBBER, Role.TROUBLEMAKER, Role.SHAMAN, Role.DRUNK,
    Role.DOPPELGANGER,  # if the Drunk is in the deck
    Role.INTRIGUER,     # if the Intriguer or Inspector or Morninger is in the deck
    Role.DOPPELGANGER,  # if the Intriguer or Inspector or Morninger is in the deck
    Role.INSPECTOR, Role.MORNINGER  # 'Kamikadze' has no night actions so it's not listed
]
'''

ROLES_DATA = [{'name_ru': 'Стражник', 'name_en': 'Guard', 'team': 'green', 'action_description_ru': 'При участии в игре Стражника, положите любой жетон или монету в центр стола при раздаче карт. Стражник просыпается первым и может положить жетон Стражника поверх любой карты на столе, кроме своей. Игроки больше не могут взаимодействовать с накрытой картой ночью. Это правило сильнее всех остальных правил.', 'action_description_en': 'When the Guard is in the game, place any token.py or coin in the center of the table when dealing cards. The Guard wakes up first and can put the Guard token.py on top of any card on the table, except his own. Players can no longer interact with the covered card at night. This rule is stronger than all other rules.'}, {'name_ru': 'Двойник', 'name_en': 'Doppelganger', 'team': 'green', 'action_description_ru': 'Двойник должен посмотреть карту другого игрока. Он становится двойником подсмотренной роли, а его собственная карта приобретает цвет этой роли до конца игры. Если он подсмотрел карту ночного действия с перемещением и/или просмотром карт (Баламут, Шаман, Провидец, Воришка), он делает предписанное немедленно; если карту команды (Вервульф, Приспешник, Тигар) — просыпается еще раз со своей новой командой, будто ему была роздана такая карта. В случае, если он подсмотрел карту, подразумевающую предутренние действия (Ревизор, Интриган, Пьяница, Жаворонок), он просыпается еще раз в отдельном временном слоте перед утром.', 'action_description_en': "The Doppelganger must look at another player's card. He becomes a doppelganger of the role he spied on, and his own card takes on the color of that role until the end of the game. If he looked at a night action card with movement and/or card viewing (Troublemaker, Shaman, Seer, Robber), he performs the prescribed action immediately; if a team card (Werewolf, Minion, Tigar) - he wakes up again with his new team, as if he was dealt such a card. If he looked at a card implying pre-morning actions (Inspector, Intriguer, Drunk, Morninger), he wakes up again in a separate time slot before morning."}, {'name_ru': 'Вожак', 'name_en': 'Alpha', 'team': 'red', 'action_description_ru': 'Вожак играет за красную команду. На своем ходу он просыпается и может посмотреть карту любого другого игрока. После этого он присоединяется к остальным Вервульфам: просыпается на их ходу (с такой же возможностью посмотреть карту в центре) и поднимает большой палец вверх на ходу Приспешника.', 'action_description_en': "The Alpha plays for the red team. On his turn, he wakes up and can look at any other player's card. After that, he joins the rest of the Werewolves: he wakes up on their turn (with the same opportunity to look at a card in the center) and raises his thumb up on the Minion's turn."}, {'name_ru': 'Вервульф', 'name_en': 'Werewolf', 'team': 'red', 'action_description_ru': 'Вервульфы играют за красную команду. Ночью они просыпаются и знакомятся. Если в этот момент проснулся только один игрок, он может посмотреть на выбор одну карту в центре стола. Также Вервульфы поднимают большой палец вверх на ходу Приспешника.', 'action_description_en': "The Werewolves play for the red team. At night they wake up and get acquainted. If only one player woke up at this moment, he can choose to look at one card in the center of the table. Also, the Werewolves raise their thumb up on the Minion's turn."}, {'name_ru': 'Приспешник', 'name_en': 'Minion', 'team': 'red', 'action_description_ru': 'Приспешник играет за красную команду, но цвет его карты — зеленый, так что он может пожертвовать собой на голосовании ради победы красной команды. На ходу Приспешника Вервульфы (и Вожак) с закрытыми глазами поднимают большие пальцы вверх. В случае отсутствия за столом красных игроков Приспешник должен не допустить мирного дня.', 'action_description_en': "The Minion plays for the red team, but the color of his card is green, so he can sacrifice himself in the vote for the victory of the red team. On the Minion's turn, the Werewolves (and the Alpha) with their eyes closed raise their thumbs up. In the absence of red players at the table, the Minion must prevent a peaceful day."}, {'name_ru': 'Тигар', 'name_en': 'Tigar', 'team': 'green', 'action_description_ru': 'Тигары играют за зеленую команду. Они могут открыть глаза и увидеть друг друга, других действий не совершают.', 'action_description_en': 'The Tigars play for the green team. They can open their eyes and see each other, they do not perform other actions.'}, {'name_ru': 'Шериф', 'name_en': 'Sheriff', 'team': 'green', 'action_description_ru': 'Шериф играет за зеленую команду. Он может посмотреть карту любого другого игрока.', 'action_description_en': "The Sheriff plays for the green team. He can look at any other player's card."}, {'name_ru': 'Провидец', 'name_en': 'Seer', 'team': 'green', 'action_description_ru': 'Провидец играет за зеленую команду. Он может посмотреть на выбор две из трех карт, лежащих в центре стола.', 'action_description_en': 'The Seer plays for the green team. He can choose to look at two of the three cards lying in the center of the table.'}, {'name_ru': 'Ревизор', 'name_en': 'Inspector', 'team': 'green', 'action_description_ru': 'Ревизор играет за зеленую команду. Он может посмотреть карту любого другого игрока. Если он подсмотрел карту Вервульфа или Приспешника, он должен немедленно объявить об этом и показать всем свою карту. Игра заканчивается, и зеленая команда побеждает.', 'action_description_en': "The Inspector plays for the green team. He can look at any other player's card. If he looked at the Werewolf or Minion card, he must immediately announce this and show everyone his card. The game ends, and the green team wins."}, {'name_ru': 'Интриган', 'name_en': 'Intriguer', 'team': 'green', 'action_description_ru': 'Интриган играет за зеленую команду. Он просыпается одним из первых и может поменять местами карты двух других игроков; а в конце ночи - просыпается ещё раз и меняет карты тех же игроков еще раз (обязательно, если была совершена первая замена карт). Интриган не смотрит перемещаемые карты.', 'action_description_en': 'The Intriguer plays for the green team. He wakes up as one of the first and can swap the cards of two other players; and at the end of the night - wakes up again and changes the cards of the same players again (mandatory if the first card replacement was made). The Intriguer does not look at the moved cards.'}, {'name_ru': 'Воришка', 'name_en': 'Robber', 'team': 'green', 'action_description_ru': 'Воришка играет за зеленую команду. Он может поменяться картой с другим игроком и посмотреть свою новую роль. Смотреть свою новую роль до замены воришка не может.', 'action_description_en': 'The Robber plays for the green team. He can swap his card with another player and look at his new role. The Robber cannot look at his new role before the swap.'}, {'name_ru': 'Баламут', 'name_en': 'Troublemaker', 'team': 'green', 'action_description_ru': 'Баламут играет за зеленую команду. Он может поменять местами карты двух других игроков. Не смотрит перемещаемые карты.', 'action_description_en': 'The Troublemaker plays for the green team. He can swap the cards of two other players. He does not look at the moved cards.'}, {'name_ru': 'Шаман', 'name_en': 'Shaman', 'team': 'green', 'action_description_ru': 'Шаман играет за зеленую команду. Он может поменять карту другого игрока с картой в центре. Не смотрит перемещаемые карты.', 'action_description_en': "The Shaman plays for the green team. He can swap another player's card with a card in the center. He does not look at the moved cards."}, {'name_ru': 'Пьяница', 'name_en': 'Drunk', 'team': 'green', 'action_description_ru': 'Пьяница играет за зеленую команду. Он должен поменять свою карту с картой в центре. Перед этим может посмотреть свою карту. Карту из центра смотреть нельзя.', 'action_description_en': 'The Drunk plays for the green team. He must swap his card with a card in the center. He can look at his card before this. He cannot look at the card from the center.'}, {'name_ru': 'Жаворонок', 'name_en': 'Morninger', 'team': 'green', 'action_description_ru': 'Жаворонок играет за зеленую команду. Он может посмотреть свою карту после всех перемещений.', 'action_description_en': 'The Morninger plays for the green team. He can look at his card after all the movements.'}, {'name_ru': 'Камикадзе', 'name_en': 'Suicidal', 'team': 'blue', 'action_description_ru': 'Камикадзе играет за синюю команду. Ночных действий он не совершает.', 'action_description_en': 'The Suicidal plays for the blue team. He does not perform any night actions.'}]
WISH_TO_UPDATE = False

ROLES_INCLUSION_ORDER = ['Вервульф', 'Камикадзе', 'Воришка', 'Баламут', 'Приспешник', 'Двойник', 'Провидец',
                         'Жаворонок',
                         'Шериф', 'Вервульф', 'Тигар', 'Тигар', 'Шаман',
                         'Интриган',
                         'Пьяница',
                         'Ревизор',
                         'Вожак', 'Стражник', 'Тигар', 'Вервульф']

NIGHT_ACTIONS_ORDER = ['Двойник', 'Стражник', 'Вожак', 'Вервульф', 'Приспешник',
                       'Тигар', 'Провидец', 'Шериф', 'Ревизор',
                       'Интриган', 'Воришка', 'Баламут', 'Шаман', 'Пьяница',
                       'Двойник',  # если в колоде пьяница
                       'Интриган',
                       'Двойник',  # если в колоде интриган или ревизор или жаворонок
                       'Ревизор', 'Жаворонок'  # , 'Камикадзе' # has no night actions
                       ]

NUM_CARDS_IN_CENTER = 3
MIN_NUM_PLAYERS = 5
MAX_NUM_PLAYERS = len(ROLES_INCLUSION_ORDER) - NUM_CARDS_IN_CENTER
MAX_NUM_ROUNDS = 10
AWARDS = {'green': 1, 'red': 1, 'blue': 1}  # points for winners



def load_data():
    # Get the absolute path to roles.json
    dir_path = os.path.dirname(os.path.realpath(__file__))
    roles_json_path = os.path.join(dir_path, 'roles.json')
    with open(roles_json_path, 'r', encoding='utf-8') as f:
        roles_data = json.load(f)
    return roles_data


def get_data():
    if WISH_TO_UPDATE:
        roles_data = load_data()
    else:
        roles_data = ROLES_DATA  # last version is manually stored here
    return roles_data
