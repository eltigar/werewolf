game_data_example = {
        'admin_id': 'user_id0',
        'status': 'created',
        'participants': {  # and scores
            'user_id1': {
                'score': 'score1',  # None before the game ends
                'username': 'username1'
                },
            'user_id2': {
                'score': 'score2',  # None before the game ends
                'username': 'username2'
                },
            },
        'setup': {
            'set_of_cards': ['card1', 'card2', 'card3']
            }
        }


user_data_example = {
    'game_history': {
        'game_id1': 'score1',
        'game_id2': 'score2'
        },
    'settings': {
        'username': 'Name123'
    }
}
