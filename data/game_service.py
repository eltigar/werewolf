import asyncio
from uuid import uuid4

from data.game_repository import GameRepository
from data.user_repository import UserRepository
from core.gameplay import play, Table
from core.global_setup import NIGHT_ACTIONS_ORDER, AWARDS


# Example Usage
# save_game_state('game123', 'created', table_object)
# game = load_table('game123', 'created')


class GameService:

    def __init__(self, user_repo: UserRepository, game_repo: GameRepository):
        self.awaiting_input: dict = {}  # all players awaiting for input
        self.user_repo = user_repo
        self.game_repo = game_repo

    def create_game(self, admin_id: str) -> str:
        admin = self.user_repo.get_user(admin_id)
        if admin is None:
            return "User not found."
        elif admin.current_game_id is not None:
            return "User already in a game"
        else:
            game_id = str(uuid4())[:6]
            current_table = Table(game_id, admin_id, status='created', cards_set=[],
                                  roles_night_order=NIGHT_ACTIONS_ORDER, players=[admin_id], awards=AWARDS)
            self.game_repo.save_game_state(game_id, current_table, status='created')  # load, add game pickle bac
            self.user_repo.update_game_id_and_status(admin_id, game_id, 'created')
            return f"Game {game_id} is created. Tap to copy: `/join {game_id}`"

    def join_game(self, user_id, game_id) -> str:
        if self.user_repo.get_user(user_id) is None:
            return "User not found."
        user = self.user_repo.get_user(user_id)
        current_game_id = user.current_game_id
        if current_game_id is not None:
            if current_game_id == game_id:
                return "User is already in this game"
            else:
                return "User is already in the other game"
        current_table = self.game_repo.load_table(game_id, 'created')
        if not current_table:
            return f"Game with ID=`{game_id}` not found in created games."
        current_table.players.append(user_id)
        self.game_repo.save_game_state(game_id, current_table, status='created')  # update created games db
        self.user_repo.update_game_id_and_status(user_id, game_id, 'created')  # update users db
        return f"User {user_id} joined game {game_id}."

    def leave_game(self, user_id) -> str:
        user = self.user_repo.get_user(user_id)
        game_id = user.current_game_id
        if not game_id:
            return "User not part of any game."
        if user.current_game_status != 'created':
            return "User cannot leave on this stage"
        current_table = self.game_repo.load_table(game_id, 'created')
        if not current_table:
            return "Table object for user not found"
        if current_table.admin_id == user_id:
            return "Admin cannot leave the game."
        current_table.players.remove(user_id)
        self.game_repo.save_game_state(game_id, current_table, status='created')  # update created games db
        self.user_repo.update_game_id_and_status(user_id, None, None)  # update users db
        return f"User {user_id} has left game {current_table.game_id}."

    def kick_player(self, admin_id, user_id_to_kick) -> str:
        user = self.user_repo.get_user(admin_id)
        game_id = user.current_game_id
        status = user.current_game_status
        if not status:
            return "User not part of any game."
        if status != 'created':
            return "Game is not on the setup stage"
        current_table = self.game_repo.load_table(game_id, 'created')
        if not current_table:
            return "Game not found."
        if current_table.admin_id != admin_id:
            return "User not Admin of the game."
        if current_table.admin_id == user_id_to_kick:
            return "Admin cannot kick himself"
        if user_id_to_kick not in current_table.players:
            return "User to kick is not a part of a game"
        current_table.players.remove(user_id_to_kick)
        self.game_repo.save_game_state(game_id, current_table, status='created')  # update created games db
        self.user_repo.update_game_id_and_status(user_id_to_kick, None, None)  # update users db
        return f"Player {user_id_to_kick} has been kicked from game {game_id}."

    def cancel_game(self, admin_id) -> str:
        user = self.user_repo.get_user(admin_id)
        game_id = user.current_game_id
        status = user.current_game_status
        if not status:
            return "User not part of any game."
        if status != 'created':
            return "Game is not on the setup stage"
        current_table = self.game_repo.load_table(game_id, 'created')
        if current_table.admin_id != admin_id:
            return "User not Admin of the game."
        current_table.admin_id = None
        for player_id in current_table.players:
            self.user_repo.update_game_id_and_status(player_id, None, None)  # update users db
        self.game_repo.move_table(game_id, 'created', 'cancelled')
        return f"Game {game_id} was cancelled by admin {admin_id}."

    def get_participants(self, game_id) -> list[int] | str:
        current_table = self.game_repo.load_table(game_id, 'created')
        return str(current_table.players) if current_table else "Game not found."

    def set_cards(self, admin_id, cards: list):
        user = self.user_repo.get_user(admin_id)
        game_id = user.current_game_id
        status = user.current_game_status
        if not status:
            return "User not part of any game."
        if status != 'created':
            return "Game is not on the setup stage"
        current_table = self.game_repo.load_table(game_id, 'created')
        if current_table.admin_id != admin_id:
            return "User not Admin of the game."
        if not cards:
            return f"Error: no cards were given"
        current_table.cards_set = cards
        self.game_repo.save_game_state(game_id, current_table, 'created')
        return f"Cards {cards} set for game {game_id}."

    def transfer_admin(self, admin_id, new_admin_id):
        user = self.user_repo.get_user(admin_id)
        game_id = user.current_game_id
        status = user.current_game_status
        if not status:
            return "User not part of any game."
        if status != 'created':
            return "Game is not on the setup stage"
        current_table = self.game_repo.load_table(game_id, 'created')
        if current_table.admin_id != admin_id:
            return "User not Admin of the game."
        if new_admin_id not in current_table.players:
            return f"New admin is not in the game"
        current_table.admin_id = new_admin_id
        self.game_repo.save_game_state(game_id, current_table)
        return f"{new_admin_id} is new Admin of the game {game_id}."

    def check_if_game_can_start(self, admin_id, game_id):
        current_table = self.game_repo.load_table(game_id, 'created')
        # Check if the game exists and the user trying to start it is the admin.
        if current_table is None:
            return "Game not found."
        if current_table.admin_id != admin_id:
            return "Only the game admin can start the game."

        # Check if the game is in the 'created' state.
        if current_table.status != 'created':
            return "Game cannot be started in its current state."

        # Check if there are enough participants to start the game.
        if len(current_table.players) < 2:  # Assuming at least 2 participants are required to start the game.
            return "Not enough participants to start the game."

        return f"Game {game_id} is starting!"

    async def start_game(self, current_table: Table):

        # usernames should be added here and other final preparation
        # for player_id in .players: .usernames.append(get_username(player_id))

        for player_id in current_table.players:
            self.user_repo.update_game_id_and_status(player_id, 'same', 'started')  # update users db
        self.game_repo.move_table(current_table.game_id, 'created', 'started')
        await play(current_table)

    def make_night_action(self, action_args: list[int] | None, current_table: Table) -> None:
        # do the action
        "perform_action(*action_args)"
        "send info"
        # if not the last turn
        if "after_next_role" != "last for a game":
            # if after_next_role do not need args
            if current_table.next_role in ['list of roles w/o args'] or current_table.players.count('Werewolf') != 1:
                # run after next immediately
                self.make_night_action(None, current_table)
            else:  # if after_next_role need args
                "inform role players"
                "get ready to receive args"
                "save state"
        else:  # if last of the game
            "go to voting:"
            "send each player notification"
            "get ready to receive votes"

        # perform, changing table if needed

        # send confirmation or info to user

        # if next action require args + send request to act
        # else make_night_action(next) just send the required info to next role, and so on
        # save state in awaited position

        pass

    def accept_vote(self, game_id: str, user_id: str, vote: str):
        # placeholder
        return f"Vote by {user_id} equals {vote} has got to the function in game service"
        pass

    def abort_game(self, game_id) -> str:
        current_table = self.game_repo.load_table(game_id, 'started')
        current_table.admin_id = None
        for player_id in current_table.players:
            self.user_repo.update_game_id_and_status(player_id, None, None)  # update users db
        self.game_repo.move_table(game_id, 'started', 'cancelled')
        return f"Game {game_id} was aborted by admin."

