from core.global_setup import NUM_CARDS_IN_CENTER
from communication.communication import get_from_player, send_to_player
cards_in_center = NUM_CARDS_IN_CENTER


#  потом надо перенаправить дату чтобы она из json шла

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
    def perform_action(self, role, *args, **kwargs):
        # Get the action function from the action map
        action_func = self.action_map.get(role)
        if action_func is not None:
            # Call the action function with any additional arguments
            action_func(*args, **kwargs)
        else:
            pass
            # raise exception

    # collecting input. May be re-routed if needed
    def get_action_args(self):
        # Get the input from the user
        inputted_args = get_from_player(self.table.performer_position, "Enter the action arguments separated by ' ': ")

        # Convert the input to a list of integers
        action_args = list(map(int, inputted_args.split()))
        return action_args

    def get_and_validate_input(self, input_format):
        while True:
            # Get the input from the user
            action_args = self.get_action_args()

            # Check if the input matches the format
            if len(action_args) != len(input_format):
                send_to_player(self.table.performer_position, "Invalid number of arguments. Please try again.")
                continue

            # Check if the input is valid
            for i, arg in enumerate(action_args):
                if not isinstance(arg, int):
                    send_to_player(self.table.performer_position, "Invalid input type. Please enter an integer.")
                    break
                elif self.table.performer_position == arg:
                    send_to_player(self.table.performer_position, "You cannot act on your own card. Please try again.")
                    break
                elif self.table.guarded_card == arg:
                    send_to_player(self.table.performer_position, "The card you entered is blocked. Please try again.")
                    break
                elif input_format[i] == 'player':
                    if not (0 <= arg < len(self.table.roles) - cards_in_center):
                        send_to_player(self.table.performer_position, "Invalid player position. Please try again.")
                        break
                elif input_format[i] == 'center':
                    if not (-cards_in_center <= arg < 0):
                        send_to_player(self.table.performer_position, "Invalid center position. Please try again.")
                        break
                elif input_format[i] == 'any':
                    if not (0 <= arg < len(self.table.roles)):
                        send_to_player(self.table.performer_position, "Invalid card position. Please try again.")
                        break
            else:  # runs in case we didn't break inside "for" loop
                # If all the arguments are unique, return them
                if len(action_args) == len(set(action_args)):
                    return action_args
                else:  # if there are repetitions in input
                    send_to_player(self.table.performer_position, "You cannot act on the same card twice. Please try again.")

    # basic actions:
    def get_card_info(self, position):  # get 0 to n-1 for players, and -1, -2, -3 for center right to left
        return self.table.cards[position]

    def swap_cards(self, position1, position2):
        self.table.cards[position1], self.table.cards[position2] = \
            self.table.cards[position2], self.table.cards[position1]

    def block_card(self, position):
        # prevent further actions on the card at the given position
        self.table.guarded_card = position

    def find_roles(self, role):
        # return a list of players who have the given role
        return [i for i in self.table.roles[:-3] if self.table.roles[i] == role]

    # actions of roles
    def doppelganger_action(self):
        self.table.doppelganger_wakeup_count += 1
        if self.table.doppelganger_wakeup_count == 1:
            # The doppelganger can look at another player's card and becomes a doppelganger of the role he spied on
            positions_to_act = self.get_and_validate_input(['player'])
            self.table.doppelganger_role = self.table.cards[positions_to_act[0]]
            send_to_player(self.table.performer_position, f"You have become a doppelganger of the role {self.table.doppelganger_role}.")

            # in case he is guard
            if self.table.doppelganger_role == 'Стражник':
                send_to_player(self.table.performer_position, "You must block Стражник now and he will not act")
                self.table.guarded_card = positions_to_act[0]

            # in case Alpha Вожак
            if self.table.doppelganger_role == 'Вожак':
                # for 'Интриган', 'Ревизор' it should be modified functiond
                self.perform_action(self.table.doppelganger_role, from_doppelganger=True)


            # in case he joins a team
            elif self.table.doppelganger_role in ['Вервульф', 'Приспешник', 'Тигар']:
                # his role is set to a new role, so he will wakeup with his new team
                send_to_player(self.table.performer_position, "Now you have to wakeup again with your new team.")
                self.table.roles[self.table.performer_position] = self.table.doppelganger_role



            # in case double actions (inspector, intriguer)
            elif self.table.doppelganger_role in ['Ревизор', 'Интриган']:
                send_to_player(self.table.performer_position, "Act first action immediately, second on a special slot")
                self.perform_action(self.table.doppelganger_role, from_doppelganger=True)

            # in case he must perform later
            elif self.table.doppelganger_role in ['Жаворонок', 'Пьяница']:
                send_to_player(self.table.performer_position, "Act your action on a special slot")
                pass  # nothing to do now

            # in case he looked at any other action card  # should be double-checked for each role
            else:
                send_to_player(self.table.performer_position, "Act immediately according to your new role")
                self.perform_action(self.table.doppelganger_role)

        elif self.table.doppelganger_wakeup_count == 2:
            if self.table.doppelganger_role == 'Пьяница':  # for the second wakeup
                self.perform_action(self.table.doppelganger_role)

        elif self.table.doppelganger_wakeup_count == 3:
            if self.table.doppelganger_role in ['Интриган', 'Ревизор', 'Жаворонок']:  # for the third wakeup
                # If the doppelganger looked at the Morninger card, he performs the Morninger's action on the third call
                if self.table.doppelganger_role == 'Жаворонок':
                    self.perform_action(self.table.doppelganger_role)
                else:
                    # for 'Интриган', 'Ревизор' it should be modified functiond
                    self.perform_action(self.table.doppelganger_role, from_doppelganger=True)

    def guard_action(self):
        if self.table.guarded_card is None:  # so he is first to act with the token.py
            # The guard can put the Guard token.py on top of any card on the table, except his own
            positions_to_act = self.get_and_validate_input(['any'])  # type = list
            self.table.guarded_card = positions_to_act[0]
            send_to_player(self.table.performer_position, f"The Guard token has been put on the card at position {positions_to_act[0]}.")
        else:  # if token.py is putted on his own card by the doppelganger
            pass

    def alpha_action(self, from_doppelganger=False):

        # The alpha can look at any other player's card
        positions_to_act = self.get_and_validate_input(['player'])
        send_to_player(self.table.performer_position, f"The card of the player at position {positions_to_act[0]} is {self.table.cards[positions_to_act[0]]}.")
        # new role to wake up on time
        self.table.roles[self.table.performer_position] = 'Вервульф'

    def werewolf_action(self):
        # The werewolves can look at each other
        werewolves_positions = [i for i, role in enumerate(self.table.roles[:-cards_in_center]) if role in ['Вервульф']]
        send_to_player(self.table.performer_position, f"The werewolves are at positions {werewolves_positions}.")

        # If there is only one werewolf, he can look at one card in the center
        if len(werewolves_positions) == 1:
            send_to_player(self.table.performer_position, "Which center card you want to know?")
            positions_to_act = self.get_and_validate_input(['center'])
            send_to_player(self.table.performer_position,
                f"The card in the center at position {positions_to_act[0]} is {self.table.cards[positions_to_act[0]]}.")

    def minion_action(self):
        # The minion can see who the werewolves are
        werewolves_positions = [i for i, role in enumerate(self.table.roles[:-cards_in_center]) if
                                role in ['Вервульф', 'Вожак']]
        send_to_player(self.table.performer_position, f"The werewolves are at positions {werewolves_positions}.")

    def tigar_action(self):
        # The tigars can see each other
        tigars_positions = [i for i, role in enumerate(self.table.roles[:-cards_in_center]) if role == 'Тигар']
        send_to_player(self.table.performer_position, f"The tigars are at positions {tigars_positions}.")

    def sheriff_action(self):
        # The sheriff can look at any other player's card
        positions_to_act = self.get_and_validate_input(['player'])
        send_to_player(self.table.performer_position, f"The card of the player at position {positions_to_act[0]} is {self.table.cards[positions_to_act[0]]}.")

    def seer_action(self):
        # The seer can look at two cards in the center
        positions_to_act = self.get_and_validate_input(['center', 'center'])
        send_to_player(self.table.performer_position,
            f"The cards in the center at positions {positions_to_act} are {self.table.cards[positions_to_act[0]]} and {self.table.cards[positions_to_act[1]]}.")

    def inspector_action(self, from_doppelganger=False):
        if from_doppelganger:
            role_positions = self.table.doppelganger_positions
        else:
            role_positions = self.table.inspector_positions

        if role_positions is None:  # for the first wakeup
            # The inspector can look at any other player's card
            role_positions = self.get_and_validate_input(['player'])
            send_to_player(self.table.performer_position, f"The card of the player at position {role_positions[0]} is {self.table.cards[role_positions[0]]}.")
        else:  # for the second wakeup
            # The inspector can look at the same player's card again
            send_to_player(self.table.performer_position, f"The card of the player at position {role_positions[0]} is {self.table.cards[role_positions[0]]}.")

        #  store positions in the correct place
        if from_doppelganger:
            self.table.doppelganger_positions = role_positions
        else:
            self.table.inspector_positions = role_positions

    def intriguer_action(self, from_doppelganger=False):
        if from_doppelganger:
            role_positions = self.table.doppelganger_positions
        else:
            role_positions = self.table.intriguer_positions

        if role_positions is None:  # for the first wakeup
            # The intriguer can swap the cards of two other players
            role_positions = self.get_and_validate_input(['player', 'player'])
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

    def robber_action(self):
        # The robber can swap his card with another player's card and look at his new role
        positions_to_act = self.get_and_validate_input(['player'])
        self.table.cards[self.table.performer_position], self.table.cards[positions_to_act[0]] = \
            self.table.cards[positions_to_act[0]], self.table.cards[self.table.performer_position]
        send_to_player(self.table.performer_position, f"You got a card of {self.table.cards[self.table.performer_position]}.")

    def troublemaker_action(self):
        # The troublemaker can swap the cards of two other players
        positions_to_act = self.get_and_validate_input(['player', 'player'])
        self.table.cards[positions_to_act[0]], self.table.cards[positions_to_act[1]] = \
            self.table.cards[positions_to_act[1]], self.table.cards[positions_to_act[0]]

    def shaman_action(self):
        # The shaman can swap another player's card with a card from the center
        positions_to_act = self.get_and_validate_input(['player', 'center'])
        self.table.cards[positions_to_act[0]], self.table.cards[positions_to_act[1]] = \
            self.table.cards[positions_to_act[1]], self.table.cards[positions_to_act[0]]

    def drunk_action(self):
        # The drunk swaps his card with a card from the center
        positions_to_act = self.get_and_validate_input(['center'])
        send_to_player(self.table.performer_position, f"You were a {self.table.cards[self.table.performer_position]} before the swap.")
        self.table.cards[self.table.performer_position], self.table.cards[positions_to_act[0]] = \
            self.table.cards[positions_to_act[0]], self.table.cards[self.table.performer_position]

    def morninger_action(self):
        # The morninger can look at his card after all the movements
        send_to_player(self.table.performer_position, f"You are a {self.table.cards[self.table.performer_position]}.")

    def suicidal_action(self):
        # The suicidal does not perform any night actions
        pass

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
