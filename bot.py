# bot.py
from aiogram import Bot, Dispatcher
from environs import Env
#  from config_data.config import Config, load_config
from handlers import in_game_handlers, game_setup_handlers, default_handlers

# Load configuration data
#  config: Config = load_config()
# Setup environment configurations
env = Env()  # Создаем экземпляр класса Env
env.read_env(
    "C:/Users/ibrau/Documents/Environmental_variables/werewolf.env")  # Методом read_env() читаем файл .env и загружаем из него переменные в окружение

BOT_TOKEN = env('BOT_TOKEN')
ADMIN_ID = env.int('ADMIN_ID')

# Initialize the bot and dispatcher
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Register routers (handlers) with the dispatcher
# dp.include_router(in_game_handlers.router)
dp.include_router(game_setup_handlers.router)
dp.include_router(default_handlers.router)

