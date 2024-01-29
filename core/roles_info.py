from collections import Counter
from core.getting_roles_info import roles_dict as ROLES_DICT

def represent_cards_set(roles_dict, cards_set):
    count = Counter(cards_set)
    representation = []
    second_wakeup_info_added = False

    # Iterate through roles_dict to maintain order
    for role_name in roles_dict:
        quantity = count.get(role_name, 0)
        if quantity > 0:
            role = roles_dict[role_name]
            role_rep = str(role)
            if role.second_wakeup:
                role_rep += "\*"
                second_wakeup_info_added = True
            if quantity > 1:
                role_rep += f" x{quantity}"
            if role.ru_name == "Камикадзе":
                role_rep += " (спит)"
            representation.append(role_rep)

    output = "Участвующие роли в порядке ночных действий:\n" + "\n".join(representation)
    if second_wakeup_info_added:
        output += "\n\*эта роль может просыпаться дважды"

    return output


def validate_cards_set(roles_dict, cards_set):
    count = Counter(cards_set)
    valid_cards_set = []
    removed_items = []

    for role_name, quantity in count.items():
        role = roles_dict.get(role_name)
        if role:
            allowed_quantity = min(quantity, role.max_quantity)
            valid_cards_set.extend([role_name] * allowed_quantity)
            if quantity > allowed_quantity:
                removed_items.append(f"{role_name} x{quantity - allowed_quantity}")
        else:
            removed_items.append(f"{role_name} x{quantity}")

    message = "Набор карт был корректен." if not removed_items else "Следующие карты были удалены: " + ", ".join(removed_items)
    return valid_cards_set, message


def complete_cards_set(given_cards_set, roles_inclusion_order, roles_dict, num_cards):
    cards_set = given_cards_set.copy()

    for role in roles_inclusion_order:
        validated_given_cards_set, message = validate_cards_set(roles_dict, given_cards_set)
        if role in given_cards_set:
            validated_given_cards_set.remove(role)  # removing from the original list to exclude double-counting
        else:
            role_count = cards_set.count(role)
            max_allowed = roles_dict[role].max_quantity
            if role_count < max_allowed:
                cards_set.append(role)
            else:
                message += f"\nРоль {role} не была добавлена, их уже {max_allowed}"

        if len(cards_set) >= num_cards:
            cards_set = cards_set[:num_cards]
            if cards_set.count('Тигар') != 1:  # Should be none or at least 2 of them
                break
            else:
                cards_set.remove('Тигар')
            # just for testing
            if num_cards == 5:
                cards_set.remove('Баламут') if 'Баламут' in cards_set else True
                cards_set.remove('Интриган') if 'Интриган' in cards_set else True
    print(message)
    return cards_set


testing = False
if testing:
    CARDS_SET = ['Жаворонок', 'Шаман', 'Шериф', 'Пьяница', 'Шаман', "увуауа", 'Вервульф', 'Вервульф',  'Вервульф',  'Вервульф', 'Вервульф', 'Двойник']
    validated_set, validation_message = validate_cards_set(ROLES_DICT, CARDS_SET)
    print(validation_message, "\n")
    text = represent_cards_set(ROLES_DICT, validated_set)
    print(text)

    """
    
    """

