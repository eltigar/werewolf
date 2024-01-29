"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Table:
    game_id: str
    admin_id: str
    status: str
    roles_night_order: List[str]
    awards: Dict
    players: List[str]
    nicknames: List[str]
    num_center = 3

def generate_table_keyboard(table: Table) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[], row_width=3)  # Adjust row width as needed

    # Add player buttons
    for position, nickname in zip(range(len(table.nicknames)), table.nicknames):
        # Using player_id as callback data, modify as needed
        button = InlineKeyboardButton(text=str(nickname), callback_data=str(position))
        keyboard.add(button)

    # Add center cards (assuming a fixed number for simplicity)
    for i in range(table.num_center):
        card_button = InlineKeyboardButton(text=f"Center {i+1}", callback_data=str(i-4))  # to get
        keyboard.add(card_button)

    return keyboard


# Mock data for testing
mock_table = Table(
    game_id="game123",
    admin_id="admin456",
    status="active",
    roles_night_order=["role1", "role2"],
    awards={"win": 10},
    players=["player1", "player2", "player3"],
    nicknames=["Alice", "Bob", "Charlie"]
)

# Testing the function
keyboard = generate_table_keyboard(mock_table)
# print(keyboard)
# Normally, you would use this 'keyboard' variable with an aiogram method to send it to the user
"""


def generate_scores_with_medals(scores: dict[str, int]):
    # Define the medals
    medals = ["🥇", "🥈", "🥉"]
    medals_left = medals.copy()
    medals_count = 0
    # Determine the unique score values
    sorted_scores = sorted(set(scores.values()), reverse=True)
    medals_dict = {}
    for top_result in sorted_scores[:3]:
        for name, score in scores.items():
            if score == top_result:
                medals_dict[name] = medals_left[0]
                medals_count += 1
        medals_left = medals[medals_count:]
        if not medals_left:
            break
    # Generate the scores text with medals
    scores_text = "The final scores are:\n" + "\n".join(f"{name}: {score}{medals_dict.get(name, '')}" for name, score in scores.items())
    return scores_text



import random


def generate_test_scores():
    num_people = 7
    num_tests = 10
    test_cases = []

    for _ in range(10):
        # Generate scores for a fixed number of people
        scores = {f"Player {i + 1}": random.randint(0, 5) for i in range(num_people)}
        test_cases.append(scores)

    # Adding edge cases manually
    # Case where all players have the same score
    test_cases.append({f"Player {i + 1}": 5 for i in range(num_people)})

    # Case where there are clear top1, top2, and top3
    test_cases.append({f"Player {i + 1}": num_people - i for i in range(num_people)})

    # Case where there are multiple top1s, no top2, and multiple top3s
    test_cases.append({"Player 1": 10, "Player 2": 10, "Player 3": 1, "Player 4": 1, "Player 5": 1,
                       "Player 6": 1, "Player 7": 1, "Player 8": 1, "Player 9": 1, "Player 10": 1})

    # Case where there are multiple top1s, top2s, and a single top3
    test_cases.append({"Player 1": 10, "Player 2": 10, "Player 3": 9, "Player 4": 9, "Player 5": 8,
                       "Player 6": 7, "Player 7": 6, "Player 8": 5, "Player 9": 4, "Player 10": 3})

    # Case where there are top1s, and all others have descending scores
    test_cases.append({"Player 1": 10, "Player 2": 10, "Player 3": 8, "Player 4": 7, "Player 5": 6,
                       "Player 6": 5, "Player 7": 4, "Player 8": 3, "Player 9": 2, "Player 10": 1})

    # Case where there are top1s, and all others have the same score
    test_cases.append({"Player 1": 10, "Player 2": 10, "Player 3": 5, "Player 4": 5, "Player 5": 5,
                       "Player 6": 5, "Player 7": 5, "Player 8": 5, "Player 9": 5, "Player 10": 5})

    return test_cases

test_cases = generate_test_scores()
for scores in test_cases:
    print(generate_scores_with_medals(scores))

print(generate_scores_with_medals({
    "Жора": 2,

    "Andrey": 3,
    "Ilya": 1,
    "Lena": 5,
    "Коля": 3,
    "oko": 6
}))