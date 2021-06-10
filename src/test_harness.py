import random

from game_implementation.disc_state import DiscState
from game_implementation.game_runner import run_games
from game_implementation.strategy import PreferTakeOnDoubleSafeDie, RandomStrategy, TallestDaisyStrategy


random_strategy = RandomStrategy()
tallest_daisy = TallestDaisyStrategy({DiscState.Gone: 3, DiscState.Safe: 2, DiscState.Vulnerable: 2})
prefer_double_take = PreferTakeOnDoubleSafeDie(
    {
        (DiscState.Gone, True): 3,
        (DiscState.Gone, False): 3,
        (DiscState.Safe, True): 1,
        (DiscState.Safe, False): 1,
        (DiscState.Vulnerable, True): 2,
        (DiscState.Vulnerable, False): 0,
    }
)


def make_strategies():
    return [
        tallest_daisy,
        prefer_double_take,
        random_strategy,
    ]


if __name__ == "__main__":
    random.seed(42)
    strategies = make_strategies()
    run_games(strategies, 1000)
