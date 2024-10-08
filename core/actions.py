import asyncio
import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.global_setup import NUM_CARDS_IN_CENTER
from data.communication import get_from_player, send_to_player, send_multiple
cards_in_center = NUM_CARDS_IN_CENTER



class Actions:
    def __init__(self, table):
        self.table = table
        # Create a dictionary mapping role names to action methods
        self.action_map = {
            'Стражник': self.guard_action,  # Guard action
            'Двойник': self.doppelganger_action,  # Doppelganger action
            'Вожак': self.alpha_action,  # Alpha action
            'Вервульф': self.werewolf_action,  # Werewolf action
            'Приспешник': self.minion_action,  # Minion action
            'Тигар': self.tigar_action,  # Tigar action
            'Провидец': self.seer_action,  # Seer action
            'Шериф': self.sheriff_action,  # Sheriff action
            'Ревизор': self.inspector_action,  # Inspector action
            'Интриган': self.intriguer_action,  # Intriguer action
            'Воришка': self.robber_action,  # Robber action
            'Баламут': self.troublemaker_action,  # Troublemaker action
            'Шаман': self.shaman_action,  # Shaman action
            'Пьяница': self.drunk_action,  # Drunk action
            'Жаворонок': self.morninger_action,  # Morninger action
            # 'Камикадзе': self.suicidal_action,  # Suicidal has no night action
        }

    # the main function running any action
    async def perform_action(self, role, *args, **kwargs):
        # Get the action function from the action map
        action_func = self.action_map.get(role)
        if action_func is not None:
            # Execute the action function directly
            await action_func(*args, **kwargs)
        else:
            raise Exception(f"Action not found for role {role}")
            # raise exception

    # collecting input. May be re-routed if needed
    async def get_action_args(self):
        # Get the input from the user
        inputted_args = await get_from_player(self.table.id_from_position(self.table.performer_position),
                                              "Ваш ход.\nВыберите карту, с которой вы хотите совершить действие:",
                                              keyboard=generate_table_keyboard(self.table))

        # Convert the input to a list of integers
        # action_args = list(map(int, inputted_args))  # it is already formatted
        return inputted_args

    async def get_and_validate_input(self, input_format):
        while True:
            # Get the input from the user
            action_args = await self.get_action_args()

            # Check if the input matches the format
            if len(action_args) != len(input_format):
                await send_to_player(self.table.id_from_position(self.table.performer_position),
                                     "Invalid number of arguments. Please try again.")
                continue

            # Check if the input is valid
            for i, arg in enumerate(action_args):
                if not isinstance(arg, int):
                    await send_to_player(self.table.id_from_position(self.table.performer_position),
                                         "Invalid input type. Please enter an integer.")
                    break
                elif self.table.performer_position == arg:
                    await send_to_player(self.table.id_from_position(self.table.performer_position),
                                         "Вы не можете выбрать свою собственную карту, попробуйте еще раз.")
                                         # "You cannot act on your own card. Please try again.")
                    break
                elif self.table.guarded_card == arg:
                    await send_to_player(self.table.id_from_position(self.table.performer_position),
                                         "The card you entered is blocked. Please try again.")
                    break
                elif input_format[i] == 'player':
                    if not (0 <= arg < len(self.table.roles) - cards_in_center):
                        await send_to_player(self.table.id_from_position(self.table.performer_position),
                                             "Invalid player position. Please try again.")
                        break
                elif input_format[i] == 'center':
                    if not (-cards_in_center <= arg < 0):
                        await send_to_player(self.table.id_from_position(self.table.performer_position),
                                             "Invalid center position. Please try again.")
                        break
                elif input_format[i] == 'any':
                    if not (0 <= arg < len(self.table.roles)):
                        await send_to_player(self.table.id_from_position(self.table.performer_position),
                                             "Invalid card position. Please try again.")
                        break
            else:  # runs in case we didn't break inside "for" loop
                # If all the arguments are unique, return them
                if len(action_args) == len(set(action_args)):
                    return action_args
                else:  # if there are repetitions in input
                    await send_to_player(self.table.id_from_position(self.table.performer_position),
                                         "Вы выбрали одну карту дважды. Попробуйте еще раз.")
                                         # "You cannot act on the same card twice. Please try again.")

    # basic actions:
    def get_card_info(self, position):  # get 0 to n-1 for players, and -1, -2, -3 for center right to left
        return self.table.cards[position]

    def get_name(self, position):
        return self.table.nicknames[position]

    def swap_cards(self, position1, position2):
        self.table.cards[position1], self.table.cards[position2] = \
            self.table.cards[position2], self.table.cards[position1]

    def block_card(self, position):
        # prevent further actions on the card at the given position
        self.table.guarded_card = position

    def find_roles(self, role):
        # return a list of players who have the given role
        return [i for i in self.table.roles[:-cards_in_center] if self.table.roles[i] == role]

    # actions of roles
    async def doppelganger_action(self):
        self.table.doppelganger_wakeup_count += 1
        if self.table.doppelganger_wakeup_count == 1:
            # The doppelganger can look at another player's card and becomes a doppelganger of the role he spied on
            positions_to_act = await self.get_and_validate_input(['player'])
            self.table.doppelganger_role = self.table.cards[positions_to_act[0]]
            await send_to_player(self.table.id_from_position(self.table.performer_position),
                                 f"You have become a doppelganger of the role {self.table.doppelganger_role}.")

            from data import game_service
            game_service.game_repo.save_game_state(self.table.game_id, self.table, 'started')
            # in case he is guard
            if self.table.doppelganger_role == 'Стражник':
                await send_to_player(self.table.id_from_position(self.table.performer_position),
                                     "You must block Стражник now and he will not act")
                self.table.guarded_card = positions_to_act[0]

            # in case Alpha Вожак
            elif self.table.doppelganger_role == 'Вожак':
                # for 'Интриган', 'Ревизор' it should be modified functiond
                await self.perform_action(self.table.doppelganger_role, from_doppelganger=True)


            # in case he joins a team
            elif self.table.doppelganger_role in ['Вервульф', 'Приспешник', 'Тигар']:
                # his role is set to a new role, so he will wakeup with his new team
                await send_to_player(self.table.id_from_position(self.table.performer_position),
                                     "Now you have to wakeup again with your new team.")
                self.table.roles[self.table.performer_position] = self.table.doppelganger_role



            # in case double actions (inspector, intriguer)
            elif self.table.doppelganger_role in ['Ревизор', 'Интриган']:
                await send_to_player(self.table.id_from_position(self.table.performer_position),
                                     "Act first action immediately, second on a special slot")
                await self.perform_action(self.table.doppelganger_role, from_doppelganger=True)

            # in case he must perform later
            elif self.table.doppelganger_role in ['Жаворонок', 'Пьяница']:
                await send_to_player(self.table.id_from_position(self.table.performer_position),
                                     "Act your action on a special slot")
                pass  # nothing to do now

            elif self.table.doppelganger_role == 'Камикадзе':
                await send_to_player(self.table.id_from_position(self.table.performer_position),
                                     "You do not have any night actions. To win any of Suicidal must be executed")

            # in case he looked at any other action card  # should be double-checked for each role
            else:
                await send_to_player(self.table.id_from_position(self.table.performer_position),
                                     "Act immediately according to your new role")
                await self.perform_action(self.table.doppelganger_role)

        elif self.table.doppelganger_wakeup_count == 2:  # for the second wakeup after real intriguer
            if self.table.doppelganger_role in ['Жаворонок', 'Пьяница']:  # for the second wakeup
                await self.perform_action(self.table.doppelganger_role)
            if self.table.doppelganger_role in ['Интриган', 'Ревизор']:
                # for 'Интриган', 'Ревизор' we must pass extra argument
                await self.perform_action(self.table.doppelganger_role, from_doppelganger=True)

    async def guard_action(self):
        if self.table.guarded_card is None:  # so he is first to act with the token.py
            # The guard can put the Guard token.py on top of any card on the table, except his own
            positions_to_act = await self.get_and_validate_input(['any'])  # type = list
            self.table.guarded_card = positions_to_act[0]
            await send_to_player(self.table.id_from_position(self.table.performer_position),
                                 f"The Guard token has been put on the card of {self.get_name(positions_to_act[0])}.")
        else:  # if token.py is putted on his own card by the doppelganger
            pass

    async def alpha_action(self, from_doppelganger=False):

        # The alpha can look at any other player's card
        positions_to_act = await self.get_and_validate_input(['player'])
        await send_to_player(self.table.id_from_position(self.table.performer_position),
                             f"The card of the player {self.get_name(positions_to_act[0])} is {self.table.cards[positions_to_act[0]]}.")
        # new role to wake up on time
        self.table.roles[self.table.performer_position] = 'Вервульф'

    async def werewolf_action(self):
        # The werewolves can look at each other
        werewolves_names = [self.get_name(i) for i, role in enumerate(self.table.roles[:-cards_in_center])
                            if role in ['Вервульф', 'Вожак']]
        await send_to_player(self.table.id_from_position(self.table.performer_position),
                             f"The werewolves are {', '.join(werewolves_names)}.")

        # If there is only one werewolf, he can look at one card in the center
        if len(werewolves_names) == 1:
            await send_to_player(self.table.id_from_position(self.table.performer_position),
                                 "Which center card you want to know?")
            positions_to_act = await self.get_and_validate_input(['center'])
            await send_to_player(self.table.id_from_position(self.table.performer_position),
                                 f"The card in the center at position {positions_to_act[0] + 1} is {self.table.cards[positions_to_act[0]]}.")

    async def minion_action(self):
        # The minion can see who the werewolves are
        werewolves_names = [self.get_name(i) for i, role in enumerate(self.table.roles[:-cards_in_center]) if
                                role in ['Вервульф', 'Вожак']]
        if not werewolves_names:
            answer = "There are no Werewolfs"
        else:
            answer = f"The werewolves are {', '.join(werewolves_names)}."
        await send_to_player(self.table.id_from_position(self.table.performer_position), answer)

    async def tigar_action(self):
        # The tigars can see each other
        tigars_names = [self.get_name(i) for i, role in enumerate(self.table.roles[:-cards_in_center]) if role == 'Тигар']
        await send_to_player(self.table.id_from_position(self.table.performer_position),
                             f"The Tigars are {', '.join(tigars_names)}.")

    async def sheriff_action(self):
        # The sheriff can look at any other player's card
        positions_to_act = await self.get_and_validate_input(['player'])
        await send_to_player(self.table.id_from_position(self.table.performer_position),
                             f"The card of the player {self.get_name(positions_to_act[0])} is {self.table.cards[positions_to_act[0]]}.")

    async def seer_action(self):
        # The seer can look at two cards in the center
        positions_to_act = await self.get_and_validate_input(['center', 'center'])
        formatted_positions = [str(pos + 4) for pos in positions_to_act]
        for position in positions_to_act:
            position += 1
        await send_to_player(self.table.id_from_position(self.table.performer_position),
                             f"The cards in the center at positions {', '.join(formatted_positions)} are {self.table.cards[positions_to_act[0]]} and {self.table.cards[positions_to_act[1]]}.")

    async def inspector_action(self, from_doppelganger=False):
        if from_doppelganger:
            role_positions = self.table.doppelganger_positions
        else:
            role_positions = self.table.inspector_positions

        if role_positions is None:  # for the first wakeup
            # The inspector can look at any other player's card
            role_positions = await self.get_and_validate_input(['player'])
            await send_to_player(self.table.id_from_position(self.table.performer_position),
                                 f"The card of the player {self.get_name(role_positions[0])} is {self.table.cards[role_positions[0]]}.")
        else:  # for the second wakeup
            # The inspector can look at the same player's card again
            await send_to_player(self.table.id_from_position(self.table.performer_position),
                                 f"The card of the player {self.get_name(role_positions[0])} is {self.table.cards[role_positions[0]]}.")

        #  store positions in the correct place
        if from_doppelganger:
            self.table.doppelganger_positions = role_positions
        else:
            self.table.inspector_positions = role_positions

    async def intriguer_action(self, from_doppelganger=False):
        if from_doppelganger:
            role_positions = self.table.doppelganger_positions
        else:
            role_positions = self.table.intriguer_positions

        if role_positions is None:  # for the first wakeup
            # The intriguer can swap the cards of two other players
            role_positions = await self.get_and_validate_input(['player', 'player'])
            self.table.cards[role_positions[0]], self.table.cards[role_positions[1]] = \
                self.table.cards[role_positions[1]], self.table.cards[role_positions[0]]
        else:  # for the second wakeup
            # The intriguer must swap the same cards again
            self.table.cards[role_positions[0]], self.table.cards[role_positions[1]] = \
                self.table.cards[role_positions[1]], self.table.cards[role_positions[0]]

        #  store positions in the correct place
        if from_doppelganger:
            self.table.doppelganger_positions = role_positions
        else:
            self.table.intriguer_positions = role_positions

    async def robber_action(self):
        # The robber can swap his card with another player's card and look at his new role
        positions_to_act = await self.get_and_validate_input(['player'])
        self.table.cards[self.table.performer_position], self.table.cards[positions_to_act[0]] = \
            self.table.cards[positions_to_act[0]], self.table.cards[self.table.performer_position]
        await send_to_player(self.table.id_from_position(self.table.performer_position),
                             f"You got a card of {self.table.cards[self.table.performer_position]}.")

    async def troublemaker_action(self):
        # The troublemaker can swap the cards of two other players
        positions_to_act = await self.get_and_validate_input(['player', 'player'])
        self.table.cards[positions_to_act[0]], self.table.cards[positions_to_act[1]] = \
            self.table.cards[positions_to_act[1]], self.table.cards[positions_to_act[0]]

    async def shaman_action(self):
        # The shaman can swap another player's card with a card from the center
        positions_to_act = await self.get_and_validate_input(['player', 'center'])
        self.table.cards[positions_to_act[0]], self.table.cards[positions_to_act[1]] = \
            self.table.cards[positions_to_act[1]], self.table.cards[positions_to_act[0]]

    async def drunk_action(self):
        # The drunk swaps his card with a card from the center
        await send_to_player(self.table.id_from_position(self.table.performer_position),
                             f"You were a {self.table.cards[self.table.performer_position]} before the swap.")
        positions_to_act = await self.get_and_validate_input(['center'])
        self.table.cards[self.table.performer_position], self.table.cards[positions_to_act[0]] = \
            self.table.cards[positions_to_act[0]], self.table.cards[self.table.performer_position]

    async def morninger_action(self):
        # The morninger can look at his card after all the movements
        await send_to_player(self.table.id_from_position(self.table.performer_position),
                             f"You are a {self.table.cards[self.table.performer_position]}.")

    async def suicidal_action(self):
        # The suicidal does not perform any night actions
        pass


def generate_table_keyboard(table) -> InlineKeyboardMarkup:

    # Add player buttons
    player_buttons = []
    for position, nickname in zip(range(len(table.nicknames)), table.nicknames):
        # Using player_id as callback data, modify as needed
        button = InlineKeyboardButton(text=str(nickname), callback_data=str(position))
        player_buttons.append(button)

    center_buttons = []
    # Add center cards (assuming a fixed number for simplicity)
    for i in range(table.num_center):
        button = InlineKeyboardButton(text=f"Центр {i+1}", callback_data=str(i-3))  # to get -3 -2 -1
        center_buttons.append(button)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[player_buttons, center_buttons])
    return keyboard

# print(get_night_order(complete_cards_set([], 150)))
# roles_dict = {}
# Load the roles once at the start of your program
# print(roles_dict)
# Create a dictionary mapping role names to role objects
# order = get_night_order(['Вервульф', 'Камикадзе', 'Воришка', 'Баламут', 'Приспешник', 'Двойник', 'Провидец', 'Жаворонок', 'Шериф', 'Вервульф'])
# print(order)
# Now you can use roles_dict to access the Role objects by name
# print(roles_dict["Стражник"].team)  # This will print "green"


#  print(load_roles().__repr__())
