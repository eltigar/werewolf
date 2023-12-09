import os
import pickle

from core.gameplay import Table


class GameRepository:
    def save_game_state(self, game_id: str, table_object: Table, status: str) -> None:
        filename = self.get_filename_based_on_status(status)
        game_tables = self.load_all_tables(status)  # Load existing states

        game_tables[game_id] = table_object
        with open(filename, 'wb') as f:
            pickle.dump(game_tables, f)

    def load_table(self, game_id, status) -> Table:
        game_tables = self.load_all_tables(status)
        return game_tables.get(game_id)

    def move_table(self, game_id: str, from_status: str, to_status: str) -> None:
        # Load the current state
        current_tables = self.load_all_tables(from_status)
        # Check if the game exists in the current state
        if game_id in current_tables:
            # Load the target state
            target_tables = self.load_all_tables(to_status)
            # Move the game
            target_tables[game_id] = current_tables.pop(game_id)  # pop both remove and return object
            target_tables[game_id].status = to_status
            # Save the updated states
            self.save_tables(current_tables, from_status)
            self.save_tables(target_tables, to_status)

    def save_tables(self, tables: dict, status: str) -> None:
        filename = self.get_filename_based_on_status(status)
        with open(filename, 'wb') as f:
            pickle.dump(tables, f)

    def load_all_tables(self, status) -> dict[str:Table]:
        filename = self.get_filename_based_on_status(status)
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                try:
                    return pickle.load(f)
                except EOFError:
                    return {}  # Return an empty dictionary if file is empty
        else:
            return {}  # Return an empty dictionary if file doesn't exist

    def get_filename_based_on_status(self, status):
        if status == "created":
            return 'created_games.pkl'
        elif status == "started":
            return 'started_games.pkl'
        elif status == "cancelled" or "aborted":
            return 'canceled_and_aborted_games.pkl'
        else:
            raise ValueError("Invalid game status")


'''
class GameRepository:
    def __init__(self, started_db, created_db, completed_db):
        self.started_db = started_db
        self.created_db = created_db
        self.completed_db = completed_db

    def get_game(self, game_id):
        game = (self.started_db.data.get(game_id) or
                self.created_db.data.get(game_id) or
                self.completed_db.data.get(game_id))
        return game

    def save_game(self, game):  # Saves to the db corresponding to game status
        # Dynamically get the database attribute based on the game status
        targeted_db = getattr(self, str(game.status) + '_db')
        # Use the dynamically retrieved database to update the data
        targeted_db.data[game.game_id] = game
        # Call the save_data method on the targeted database
        targeted_db.save_data()

    def abort_game(self, game_id):
        if game_id in self.created_db.data:
            del self.created_db.data[game_id]
            self.created_db.save_data()
        elif game_id in self.started_db.data:
            del self.started_db.data[game_id]
            self.started_db.save_data()

    def get_game_id_for_user(self, user_id, status='started') -> int or None:
        # Убеждаемся, что статус имеет одно из трёх допустимых значений
        if status not in ['created', 'started', 'completed']:
            raise ValueError("Invalid status value")
        targeted_db = getattr(self, f"{status}_db")
        for game_id, game in targeted_db.data.items():
            if user_id in game.participants:
                return game_id

        return None

'''
