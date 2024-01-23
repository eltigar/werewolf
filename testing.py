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
print(keyboard)
# Normally, you would use this 'keyboard' variable with an aiogram method to send it to the user
