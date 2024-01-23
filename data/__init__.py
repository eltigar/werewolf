# This code goes into the `data/__init__.py` module.

# from .models import Database
from data.user_repository import UserRepository
from data.game_repository import GameRepository
from data.game_service import GameService


"""
# Инициализация баз данных
# Для хранения между сессиями бота
users_db = Database('OLD_users_data.pkl')
completed_games = Database('OLD_games_data.pkl')
# Для использования во время работы бота
created_games = Database('created_games.pkl')
started_games = Database('started_games.pkl')
"""

# Инициализация репозиториев
user_repo = UserRepository()
game_repo = GameRepository()


# Инициализация сервисов
game_service = GameService(user_repo, game_repo)


manual_update = False
if __name__ == '__main__' and manual_update is True:
    game_service.user_repo.update_game_id_and_status_for_user('346858079', None, None)
    game_service.user_repo.update_game_id_and_status_for_user('301862148', None, None)