import json
from dataclasses import dataclass

# main data in russian & translation to english
ROLES_DATA = [{'name': 'Стражник', 'description': 'При участии в игре Стражника, положите любой жетон или монету в центр стола при раздаче карт. Стражник просыпается первым и может положить жетон Стражника поверх любой карты на столе, кроме своей. Игроки больше не могут взаимодействовать с накрытой картой ночью. Это правило сильнее всех остальных правил.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '🛡', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Двойник', 'description': 'Двойник должен посмотреть карту другого игрока. Он становится двойником подсмотренной роли, а его собственная карта приобретает цвет этой роли до конца игры. Если он подсмотрел карту ночного действия с перемещением и/или просмотром карт (Баламут, Шаман, Провидец, Воришка), он делает предписанное немедленно; если карту команды (Вервульф, Приспешник, Тигар) — просыпается еще раз со своей новой командой, будто ему была роздана такая карта. В случае, если он подсмотрел карту, подразумевающую предутренние действия (Ревизор, Интриган, Пьяница, Жаворонок), он просыпается еще раз в отдельном временном слоте перед утром.', 'team': 'green', 'team_emoji': '◽️', 'emoji': '🎭', 'second_wakeup': True, 'max_quantity': 1}, {'name': 'Вожак', 'description': 'Вожак играет за красную команду. На своем ходу он просыпается и может посмотреть карту любого другого игрока. После этого он присоединяется к остальным Вервульфам: просыпается на их ходу (с такой же возможностью посмотреть карту в центре) и поднимает большой палец вверх на ходу Приспешника.', 'team': 'red', 'team_emoji': '🔻', 'emoji': '🐺', 'second_wakeup': True, 'max_quantity': 1}, {'name': 'Вервульф', 'description': 'Вервульфы играют за красную команду. Ночью они просыпаются и знакомятся. Если в этот момент проснулся только один игрок, он может посмотреть на выбор одну карту в центре стола. Также Вервульфы поднимают большой палец вверх на ходу Приспешника.', 'team': 'red', 'team_emoji': '🔻', 'emoji': '🐺', 'second_wakeup': False, 'max_quantity': 3}, {'name': 'Приспешник', 'description': 'Приспешник играет за красную команду, но цвет его карты — зеленый, так что он может пожертвовать собой на голосовании ради победы красной команды. На ходу Приспешника Вервульфы (и Вожак) с закрытыми глазами поднимают большие пальцы вверх. В случае отсутствия за столом красных игроков Приспешник должен не допустить мирного дня.', 'team': 'red', 'team_emoji': '🔻', 'emoji': '👥', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Тигар', 'description': 'Тигары играют за зеленую команду. Они могут открыть глаза и увидеть друг друга, других действий не совершают.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '🦁', 'second_wakeup': False, 'max_quantity': 3}, {'name': 'Шериф', 'description': 'Шериф играет за зеленую команду. Он может посмотреть карту любого другого игрока.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '👮\u200d♂️', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Провидец', 'description': 'Провидец играет за зеленую команду. Он может посмотреть на выбор две из трех карт, лежащих в центре стола.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '👁', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Ревизор', 'description': 'Ревизор играет за зеленую команду. Он может посмотреть карту любого другого игрока. Если он подсмотрел карту Вервульфа или Приспешника, он должен немедленно объявить об этом и показать всем свою карту. Игра заканчивается, и зеленая команда побеждает.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '🕵️', 'second_wakeup': True, 'max_quantity': 1}, {'name': 'Интриган', 'description': 'Интриган играет за зеленую команду. Он просыпается одним из первых и может поменять местами карты двух других игроков; а в конце ночи - просыпается ещё раз и меняет карты тех же игроков еще раз (обязательно, если была совершена первая замена карт). Интриган не смотрит перемещаемые карты.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '🧶', 'second_wakeup': True, 'max_quantity': 1}, {'name': 'Воришка', 'description': 'Воришка играет за зеленую команду. Он может поменяться картой с другим игроком и посмотреть свою новую роль. Смотреть свою новую роль до замены воришка не может.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '👝', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Баламут', 'description': 'Баламут играет за зеленую команду. Он может поменять местами карты двух других игроков. Не смотрит перемещаемые карты.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '🌚', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Шаман', 'description': 'Шаман играет за зеленую команду. Он может поменять карту другого игрока с картой в центре. Не смотрит перемещаемые карты.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '💆', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Пьяница', 'description': 'Пьяница играет за зеленую команду. Он должен поменять свою карту с картой в центре. Перед этим может посмотреть свою карту. Карту из центра смотреть нельзя.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '🍻', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Жаворонок', 'description': 'Жаворонок играет за зеленую команду. Он может посмотреть свою карту после всех перемещений.', 'team': 'green', 'team_emoji': '🟢', 'emoji': '⏰', 'second_wakeup': False, 'max_quantity': 1}, {'name': 'Камикадзе', 'description': 'Камикадзе играет за синюю команду. Ночных действий он не совершает.', 'team': 'blue', 'team_emoji': '🔷', 'emoji': '💀', 'second_wakeup': False, 'max_quantity': 1}]
TRANSLATIONS_DATA = {'en': {'Стражник': {'name': 'Guard', 'description': 'When the Guard is in the game, place any token or coin in the center of the table when dealing cards. The Guard wakes up first and can put the Guard token on top of any card on the table, except his own. Players can no longer interact with the covered card at night. This rule is stronger than all other rules.'}, 'Двойник': {'name': 'Doppelganger', 'description': "The Doppelganger must look at another player's card. He becomes a doppelganger of the role he spied on, and his own card takes on the color of that role until the end of the game. If he looked at a night action card with movement and/or card viewing (Troublemaker, Shaman, Seer, Robber), he performs the prescribed action immediately; if a team card (Werewolf, Minion, Tigar) - he wakes up again with his new team, as if he was dealt such a card. If he looked at a card implying pre-morning actions (Inspector, Intriguer, Drunk, Morninger), he wakes up again in a separate time slot before morning."}, 'Вожак': {'name': 'Alpha', 'description': "The Alpha plays for the red team. On his turn, he wakes up and can look at any other player's card. After that, he joins the rest of the Werewolves: he wakes up on their turn (with the same opportunity to look at a card in the center) and raises his thumb up on the Minion's turn."}, 'Вервульф': {'name': 'Werewolf', 'description': "The Werewolves play for the red team. At night they wake up and get acquainted. If only one player woke up at this moment, he can choose to look at one card in the center of the table. Also, the Werewolves raise their thumb up on the Minion's turn."}, 'Приспешник': {'name': 'Minion', 'description': "The Minion plays for the red team, but the color of his card is green, so he can sacrifice himself in the vote for the victory of the red team. On the Minion's turn, the Werewolves (and the Alpha) with their eyes closed raise their thumbs up. In the absence of red players at the table, the Minion must prevent a peaceful day."}, 'Тигар': {'name': 'Tigar', 'description': 'The Tigars play for the green team. They can open their eyes and see each other, they do not perform other actions.'}, 'Шериф': {'name': 'Sheriff', 'description': "The Sheriff plays for the green team. He can look at any other player's card."}, 'Провидец': {'name': 'Seer', 'description': 'The Seer plays for the green team. He can choose to look at two of the three cards lying in the center of the table.'}, 'Ревизор': {'name': 'Inspector', 'description': "The Inspector plays for the green team. He can look at any other player's card. If he looked at the Werewolf or Minion card, he must immediately announce this and show everyone his card. The game ends, and the green team wins."}, 'Интриган': {'name': 'Intriguer', 'description': 'The Intriguer plays for the green team. He wakes up as one of the first and can swap the cards of two other players; and at the end of the night - wakes up again and changes the cards of the same players again (mandatory if the first card replacement was made). The Intriguer does not look at the moved cards.'}, 'Воришка': {'name': 'Robber', 'description': 'The Robber plays for the green team. He can swap his card with another player and look at his new role. The Robber cannot look at his new role before the swap.'}, 'Баламут': {'name': 'Troublemaker', 'description': 'The Troublemaker plays for the green team. He can swap the cards of two other players. He does not look at the moved cards.'}, 'Шаман': {'name': 'Shaman', 'description': "The Shaman plays for the green team. He can swap another player's card with a card in the center. He does not look at the moved cards."}, 'Пьяница': {'name': 'Drunk', 'description': 'The Drunk plays for the green team. He must swap his card with a card in the center. He can look at his card before this. He cannot look at the card from the center.'}, 'Жаворонок': {'name': 'Morninger', 'description': 'The Morninger plays for the green team. He can look at his card after all the movements.'}, 'Камикадзе': {'name': 'Suicidal', 'description': 'The Suicidal plays for the blue team. He does not perform any night actions.'}}}
update_data = False
# last updated 2024-01-28

# Выбор языка
language: str = 'ru'

if update_data:  # variables above should be manually updated
    # Загрузка данных о ролях из файла
    file_path = 'roles.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        ROLES_DATA = json.load(file)
    print(ROLES_DATA)

    # Загрузка данных о переводах из файла
    translations_file_path = 'translations.json'
    with open(translations_file_path, 'r', encoding='utf-8') as file:
        TRANSLATIONS_DATA: dict = json.load(file)
    print(TRANSLATIONS_DATA)

# Список доступных для перевода языков
LANG_LIST = TRANSLATIONS_DATA.keys()




# Создание dataclass для хранения информации о ролях
@dataclass
class Role:
    name: str
    description: str
    team: str
    team_emoji: str
    emoji: str
    second_wakeup: bool
    max_quantity: int
    lang: str = "ru"

    def __post_init__(self):
        self.ru_name = self.name  # so all langs have main lang nae inside
        if self.lang in LANG_LIST:
            translated_role_data = TRANSLATIONS_DATA.get(self.lang, {}).get(self.name, {})
            self.name = translated_role_data.get('name', self.name)
            self.description = translated_role_data.get('description', self.description)

    def __str__(self):
        return f"{self.team_emoji} *{self.name}*"

    def __repr__(self):
        return (f"Role(name={self.name}:description={self.description}, team={self.team}, "
                f"team_emoji={self.team_emoji}, emoji={self.emoji}, second_wakeup={self.second_wakeup}, "
                f"max_quantity={self.max_quantity})")


def create_objects_dict(roles_data):
    return {role.ru_name: role for role in [Role(**role_data, lang=language) for role_data in roles_data]}


roles_dict: dict[str, Role] = create_objects_dict(ROLES_DATA)


test = False
if test:
    roles_dict = create_objects_dict(ROLES_DATA)
    en_roles_dict = {role.ru_name: role for role in [Role(**role_data, lang='en') for role_data in ROLES_DATA]}
    # print("\n".join(str(role.ru_name) for role in roles_dict.values()))
    # print("\n".join(str(role.ru_name) for role in en_roles_dict.values()))
    # print(roles_dict)
    # print(en_roles_dict)
    print(ROLES_DATA)
    print(TRANSLATIONS_DATA)

