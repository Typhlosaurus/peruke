from typing import Protocol, Sequence

from game_implementation.action import Action
from game_implementation.board import Board
from game_implementation.dice import get_dice, get_unique_dice
from game_implementation.disc_state import DiscState


class Strategy(Protocol):
    def choose_actions(self, player_id: int, dice: Sequence[int]) -> Sequence[Action]:
        pass


class Game:
    def __init__(self, players_count: int, start_player: int):
        self.player_count = players_count
        self.board = Board(players_count)
        self.turn = 0
        self.round = 0
        self.start_player = start_player
        self.player_id = start_player

    def __repr__(self):
        return "\n".join(
            [
                f"Round: {self.round}, Turn: {self.turn}",
                f"{self.board}",
                f"Game Scores: {[player.score for player in self.board.players]}",
            ]
        )

    def play_turn(self, player_id: int, action: Action) -> bool:
        self.board.take_action(player_id, action)
        return self.board.is_round_over()

    def take_turn(self, player_id: int, strategy: Strategy) -> bool:
        dice = get_dice()
        for action in strategy.choose_actions(player_id, dice):
            self.play_turn(player_id, action)

        self.turn += 1

        return self.board.is_round_over()

    def update_end_of_round_scores(self, winner: int) -> None:
        self.board.score_round(winner)

    def end_round(self, winner_id: int) -> bool:
        self.update_end_of_round_scores(winner_id)
        self.board.reset()
        self.round += 1
        self.turn = 0
        return self.round >= self.player_count

    def set_initial_defence(self):
        for player_id in range(self.player_count):
            dice = get_unique_dice()
            for d in dice:
                self.play_turn(player_id, Action(player_id, d, DiscState.Safe))

    def winners(self) -> Sequence[int]:
        winning_score = max([player.score for player in self.board.players])
        return [
            player_idx
            for player_idx, player in enumerate(self.board.players)
            if player.score == winning_score
        ]

    def play(self, strategies: Sequence[Strategy]) -> Sequence[int]:
        print("Initial board")
        print(self, "\n", "Start Player:", self.start_player, "\n")

        while True:
            if self.turn == 0:
                print("Initial defensive rolls")
                self.set_initial_defence()
            print(self, "\n")
            self.player_id = (self.player_id + 1) % self.player_count
            player_has_won = self.take_turn(self.player_id, strategies[self.player_id])

            if player_has_won:
                print(self)
                print()
                game_has_ended = self.end_round(winner_id=self.player_id)
                if game_has_ended:
                    break

        winners = self.winners()
        print("\nEnd of game\nWinners: ", winners)

        return winners
