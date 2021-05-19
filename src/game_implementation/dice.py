from random import randrange
from typing import Sequence


def get_dice() -> Sequence[int]:
    dice = [randrange(0, 6) for _ in range(3)]
    print(f"Dice: {[d + 1 for d in dice]}")
    return dice


def get_unique_dice() -> Sequence[int]:
    # For initial safety round. Should this be 3 dice, or as many as are unique?
    return {*get_dice()}
