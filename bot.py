# bot.py
from aiogram import Bot, Dispatcher, Router

from environs import Env
from config import path_to_env
from handlers import started_game_handlers, created_game_handlers, default_handlers

# Setup environment configurations
env = Env()  # Создаем экземпляр класса Env
env.read_env(path_to_env)  # Методом read_env() читаем файл .env и загружаем из него переменные в окружение

BOT_TOKEN = env('BOT_TOKEN')
ADMIN_ID = env.int('ADMIN_ID')

# Initialize the bot and dispatcher
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# Register routers (handlers) with the dispatcher
dp.include_router(started_game_handlers.router)
dp.include_router(created_game_handlers.router)
dp.include_router(default_handlers.router)




