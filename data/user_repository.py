from data.models import User

import pickle
import os

def save_user_data(user_id: str, user_object: User):
    users = load_all_users()
    users[user_id] = user_object
    with open('users.pkl', 'wb') as f:
        pickle.dump(users, f)

def load_user_data(user_id: str) -> User:
    users = load_all_users()
    return users.get(user_id)

def load_all_users() -> dict[str, User]:
    if os.path.exists('users.pkl'):
        with open('users.pkl', 'rb') as f:
            try:
                return pickle.load(f)
            except EOFError:
                return {}
    else:
        return {}

# Example Usage
# save_user_data('user123', user_object)
# user = load_user_data('user123')


class UserRepository:

    def add_user(self, user_id, username):
        if load_user_data(user_id) is None:
            user = User(user_id, username)
            save_user_data(user_id, user)

    def get_user(self, user_id: str):
        return load_user_data(user_id)

    def update_name(self, user_id, new_name):
        user = self.get_user(user_id)
        if user:
            user.username = new_name
            save_user_data(user_id, user)

    def get_nickname(self, user_id):
        user = self.get_user(user_id)
        return user.username if user else None

    def get_game_id_for_user(self, user_id: str, status: str='started') -> str or None:
        # Убеждаемся, что статус имеет одно из допустимых значений
        if status not in ['created', 'started', 'completed', 'cancelled', 'aborted']:
            raise ValueError("Invalid status value")
        else:
            user = load_user_data(user_id)
            if user.current_game_status == status:
                return user.current_game_id
            else:  # for other statuses, including None
                return None

    def update_game_id_and_status_for_user(self, user_id: str, game_id: str | None, status: str | None) -> None:
        if status not in ['created', 'started', 'completed', 'cancelled', 'aborted', None]:
            raise ValueError("Invalid status value")
        else:
            user = load_user_data(user_id)
            if game_id != 'same':
                user.current_game_id = game_id
            user.current_game_status = status
            save_user_data(user_id, user)

    def save_user(self, user):
        save_user_data(user.user_id, user)