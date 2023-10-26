import random

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from environs import Env
from aiogram.types import InputTextMessageContent, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, \
    InlineKeyboardMarkup

# from aiogram.dispatcher.filters import Text
# from aiogram.utils import executor

env = Env()  # Создаем экземпляр класса Env
env.read_env(
    "C:/Users/ibrau/Documents/Environmental_variables/werewolf.env")  # Методом read_env() читаем файл .env и загружаем из него переменные в окружение

BOT_TOKEN = env('BOT_TOKEN')  # Получаем и сохраняем значение переменной окружения в переменную bot_token
ADMIN_ID = env.int('ADMIN_ID')  # Получаем и преобразуем значение переменной окружения к типу int

# Вместо BOT BOT_TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# Communication Module Placeholder (Replace with your actual module)
class CommunicationModule:
    @staticmethod
    def get_from_user(user_id: int):
        return f"Received message from user {user_id}"

    @staticmethod
    def send_to_user(user_id: int, message: str):
        return message  # For now, just returning the message. Actual communication logic goes here.


# Game Handling
@dp.message(lambda message: check_status(message.from_user.id) == 'in-game')
async def in_game_handler(message: types.Message):
    response = CommunicationModule.get_from_user(message.from_user.id)
    sent_message = CommunicationModule.send_to_user(message.from_user.id, response)
    await message.answer(sent_message)


# Game Setup (Admin Only)
@dp.message(Command('new'))
async def new_game(message: types.Message):
    if is_admin(message.from_user.id):
        game_id = generate_game_id()
        join_link = f"/join {game_id}"
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        button = KeyboardButton(join_link)
        kb.add(button)
        await bot.send_message(chat_id=message.chat.id, text="Here's the link to join the game:", reply_markup=kb)


# Default Handler
@dp.message(Command('start'))
async def start_command(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("/help")
    item2 = KeyboardButton("/new")
    item3 = KeyboardButton("/join")
    item4 = KeyboardButton("/change_name")
    markup.add(item1, item2, item3, item4)
    await bot.send_message(chat_id=message.chat.id, text="Choose a command:", reply_markup=markup)


@dp.message(Command('help'))
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Help message goes here...")


@dp.message(Command('join'))
async def join_command(message: types.Message):
    # Join logic here...
    await bot.send_message(chat_id=message.chat.id, text="Joined successfully!")


@dp.message(Command('change_name'))
async def change_name_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Name changed successfully!")


# For other commands and messages
@dp.message(lambda message: True)
async def echo_all(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Unexpected message, I do nothing")


# Placeholder function to check user status
def check_status(user_id):
    # Replace with actual logic to fetch status from the pickle database
    return 'default'


# Placeholder function to check if a user is an admin
def is_admin(user_id):
    # Replace with actual logic to check admin status
    return True


# Placeholder function to generate game id
def generate_game_id():
    # Replace with your game id generation logic
    return "123456"



# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        'Привет!\nДавайте сыграем в игру "Угадай число"?\n\n'
        'Чтобы получить правила игры и список доступных '
        'команд - отправьте команду /help'
    )
    # Если пользователь только запустил бота и его нет в словаре '
    # 'users - добавляем его в словарь
    if message.from_user.id not in users:
        users[message.from_user.id] = {
            'in_game': False,
            'secret_number': None,
            'attempts': None,
            'total_games': 0,
            'wins': 0
        }


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command('help'))
async def process_help_command(message: Message):
    await message.answer(
        f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
        f'а вам нужно его угадать\nУ вас есть {15} '
        f'попыток\n\nДоступные команды:\n/help - правила '
        f'игры и список команд\n/cancel - выйти из игры\n'
        f'/stat - посмотреть статистику\n\nДавай сыграем?'
    )


# Этот хэндлер будет срабатывать на команду "/stat"
@dp.message(Command('stat'))
async def process_stat_command(message: Message):
    await message.answer(
        f'Всего игр сыграно: '
        f'{users[message.from_user.id]["total_games"]}\n'
        f'Игр выиграно: {users[message.from_user.id]["wins"]}'
    )


# Этот хэндлер будет срабатывать на команду "/cancel"
@dp.message(Command('cancel'))
async def process_cancel_command(message: Message):
    if users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = False
        await message.answer(
            'Вы вышли из игры. Если захотите сыграть '
            'снова - напишите об этом'
        )
    else:
        await message.answer(
            'А мы итак с вами не играем. '
            'Может, сыграем разок?'
        )


# Этот хэндлер будет срабатывать на согласие пользователя сыграть в игру
@dp.message(F.text.lower().in_(['да', 'давай', 'сыграем', 'игра',
                                'играть', 'хочу играть']))
async def process_positive_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['secret_number'] = get_random_number()
        users[message.from_user.id]['attempts'] = ATTEMPTS
        await message.answer(
            'Ура!\n\nЯ загадал число от 1 до 100, '
            'попробуй угадать!'
        )
    else:
        await message.answer(
            'Пока мы играем в игру я могу '
            'реагировать только на числа от 1 до 100 '
            'и команды /cancel и /stat'
        )


# Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру
@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def process_negative_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer(
            'Жаль :(\n\nЕсли захотите поиграть - просто '
            'напишите об этом'
        )
    else:
        await message.answer(
            'Мы же сейчас с вами играем. Присылайте, '
            'пожалуйста, числа от 1 до 100'
        )


# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_numbers_answer(message: Message):
    if users[message.from_user.id]['in_game']:
        if int(message.text) == users[message.from_user.id]['secret_number']:
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            users[message.from_user.id]['wins'] += 1
            await message.answer(
                'Ура!!! Вы угадали число!\n\n'
                'Может, сыграем еще?'
            )
        elif int(message.text) > users[message.from_user.id]['secret_number']:
            users[message.from_user.id]['attempts'] -= 1
            await message.answer('Мое число меньше')
        elif int(message.text) < users[message.from_user.id]['secret_number']:
            users[message.from_user.id]['attempts'] -= 1
            await message.answer('Мое число больше')

        if users[message.from_user.id]['attempts'] == 0:
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            await message.answer(
                f'К сожалению, у вас больше не осталось '
                f'попыток. Вы проиграли :(\n\nМое число '
                f'было {users[message.from_user.id]["secret_number"]}'
                f'\n\nДавайте сыграем еще?'
            )
    else:
        await message.answer('Мы еще не играем. Хотите сыграть?')


# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_answers(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer(
            'Мы же сейчас с вами играем. '
            'Присылайте, пожалуйста, числа от 1 до 100'
        )
    else:
        await message.answer(
            'Я довольно ограниченный бот, давайте '
            'просто сыграем в игру?'
        )


if __name__ == '__main__':
    dp.run_polling(bot)
