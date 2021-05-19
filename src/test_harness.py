import random

from game_implementation.disc_state import DiscState
from game_implementation.game import Game
from game_implementation.strategy import RandomStrategy, TallestDaisyStrategy


def make_strategies(game: Game):
    test_strategy = TallestDaisyStrategy(
        game, {DiscState.Gone: 3, DiscState.Safe: 1, DiscState.Vulnerable: 2}
    )
    random_strategy = RandomStrategy(game)
    return [
        random_strategy,
        test_strategy,
        random_strategy,
    ]


def run_strategies(player_count, iterations):
    winner_counts = [0] * player_count

    for i in range(iterations):
        start_player = i % player_count
        game = Game(player_count, start_player)

        winners = game.play(make_strategies(game))

        for winner in winners:
            winner_counts[winner] += 1
    print("\nWinner counts", winner_counts)


if __name__ == "__main__":
    random.seed(42)
    run_strategies(3, 1_000)
