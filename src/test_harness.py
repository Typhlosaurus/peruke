import random

from game_implementation.disc_state import DiscState
from game_implementation.game_runner import run_games
from game_implementation.strategy import RandomStrategy, TallestDaisyStrategy


def make_strategies():
    test_strategy = TallestDaisyStrategy({DiscState.Gone: 3, DiscState.Safe: 2, DiscState.Vulnerable: 2})
    random_strategy = RandomStrategy()

    return [
        random_strategy,
        test_strategy,
        random_strategy,
    ]


if __name__ == "__main__":
    random.seed(42)
    strategies = make_strategies()
    run_games(strategies, 1000)
