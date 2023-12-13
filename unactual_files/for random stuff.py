import random
import matplotlib.pyplot as plt
"""
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
n = int(input("Enter a month number (1-12): "))
print("The month abbreviation is", months[n - 1] + ".", end='')
print(f"The month abbreviation is {months[n - 1]}.")
print("The mo\nth abbreviation is", months[n - 1] + ".", sep='|||||')
"""


def pull_gold_waffle(p):
    k = 0
    waffle = False
    while not waffle:
        k = k + 1
        if random.random() < p:
            waffle = True
    return k


def pull_tank(p, guarantee=50):
    k = 0
    tank = False
    while not tank:
        k = k + 1
        if k == guarantee:
            tank = True
        if random.random() < p:
            tank = True
    return k


def pull_any_waffle(total_boxes, started_tanks_1, started_tanks_2, p_tank_1=0.024, p_tank_2_and_3=0.02, p_gold=0.001, guarantee=50):
    tank_count = started_tanks_1
    boxes_left = total_boxes
    # box_count = 0
    gold_waffle = False
    while not (gold_waffle or tank_count >= 11 or boxes_left <= 0):
        # box_count += 1
        boxes_left -= 1
        guarantee -= 1
        lottery = random.random()  # 0.1% на голд вафлю
        if lottery < p_gold:
            gold_waffle = True
        if tank_count < 5:
            p_tank = p_tank_1  # 2.4% на обычный танк
        else:
            p_tank = p_tank_2_and_3
        if guarantee == 0 or p_gold < lottery < p_gold + p_tank:
            tank_count += 1
            guarantee = 50
            if tank_count == 5:
                tank_count += started_tanks_2
    return bool(boxes_left)


if __name__ == '__main__':
    number_of_runs = 100000
    plot_x = []
    plot_y = []
    for total_boxes in range(40, 601, 40):
        result = []
        for i in range(number_of_runs):
            result.append(pull_any_waffle(total_boxes, started_tanks_1=0, started_tanks_2=1))
        chance = sum(result) / len(result) * 100
        print(f"Вероятность выбить любую вафлю за {total_boxes} коробок: {chance:.2f}%")
        plot_x.append(total_boxes)
        plot_y.append(chance)
    plt.plot(plot_x, plot_y)
    # plt.show()
