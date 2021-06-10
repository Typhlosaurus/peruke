from collections import Sequence

from game_implementation.game import Game, Strategy


def run_games(strategies: Sequence[Strategy], iterations: int):
    player_count = len(strategies)
    winner_counts = [0] * player_count

    for i in range(iterations):
        start_player = i % player_count
        game = Game(player_count=player_count, start_player=start_player)

        winners = game.play(strategies)

        for winner in winners:
            winner_counts[winner] += 1

    print("\nWinner counts", winner_counts)
