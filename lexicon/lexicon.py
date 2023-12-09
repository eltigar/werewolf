# LEXICON/LEXICON.py
LEXICON_RU = {
    '/start': 'Добро пожаловать в игру "Вервульф"! Нажмите /help, чтобы узнать команды.',

    '/help': (
        'Список всех команд:\n'
        '/start - запустить бота\n'
        '/help - помощь по командам\n'
        '/change_name <Новое имя> - изменить свое имя в игре\n'
        '/new - создать новую игру\n'
        '/join <game_id> - присоединиться к игре\n'        
        '/show_joined - показать всех игроков в игре\n'
        '/set_cards card_name_1, card_name_2, ... - установить карты для игры\n'
        '/leave - покинуть игру\n'
        '/kick <user_id> - администратор может исключить игрока\n'
        '/cancel - отменить игру (админ)\n'
        '/abort - прервать и завершить игру (админ)\n'
        '/play - начать игру'
    ),

    '/new': 'Вы создали новую игру. Поделитесь ссылкой, чтобы другие игроки могли присоединиться.',

    '/join': 'Вы успешно присоединились к игре. Ожидайте начала!',

    '/change_name_request': 'Чтобы изменить имя отправьте в чат `/change_name <Новое имя>`',
    '/change_name_success': 'Ваше имя было изменено на ',
    '/change_name_error': 'Ваше имя не было изменено, так как имя должно быть не короче 3х символов',

    '/show_joined': 'В игре присутствуют следующие игроки:\n',  # The list of players will be appended dynamically

    '/leave': 'Вы покинули игру.',

    '/abort': 'Игра была прервана администратором.',

    '/kick': 'Игрок был исключен из игры.',

    '/set_cards': 'Карты установлены для следующей игры.',

    '/play': 'Игра началась! Удачи всем игрокам!',

    'error_unexpected_message': 'Неожиданное сообщение, я ничего не делаю.'
}

# LEXICON/LEXICON.py
LEXICON_EN = {
    '/start': 'Welcome to the "Werewolf" game! Press /help to see available commands.',

    '/help': (
        'List of all commands:\n'
        '/start - initialize the bot\n'
        '/help - list of commands\n'
        '/new - create a new game\n'
        '/join <game_id> - join an existing game\n'
        '/play - start the game\n'
        '/show_joined - view all players in the game\n'
        '/leave - leave the game\n'        
        '/kick <user_id> - the admin can kick a player out\n'
        '/set_cards card_name_1, card_name_2, ... - set cards for the game\n'
        '/play - start the game\n'        
        '/abort - the admin can abort the game\n'
        '/change_name <New name> - change a name displayed in the game\n'


    ),

    '/new': 'Create a new game.Share the link for other players to join.',

    '/join': 'Join already existed game by ID. "/join <game_id>"',

    '/change_name_request': 'To change your name send "/change_name <New name>"',
    '/change_name_success': 'Your name was changed to ',
    '/change_name_error': 'Your name was not changed as it should be at least 3 characters long',

    '/show_joined': 'The following players are in the game:\n',  # The list of players will be appended dynamically

    '/leave': 'You ve left the game.',

    '/abort': 'The game was aborted by the admin.',

    '/kick': 'The player has been kicked from the game.',

    '/set_cards': 'Cards are set for the next game.',

    '/play': 'The game has started! Good luck to all players!',

    'error_unexpected_message': 'Unexpected message, I do nothing.'
}
