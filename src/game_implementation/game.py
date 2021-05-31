from typing import Dict, Protocol, Sequence

from game_implementation.action import Action
from game_implementation.dice import get_dice, get_unique_dice
from game_implementation.disc_state import DiscState
from game_implementation.player import Player


class Strategy(Protocol):
    def choose_actions(self, player_id: int, dice: Sequence[int]) -> Sequence[Action]:
        pass


class Game:
    def __init__(
        self,
        player_count: int = 3,
        start_player: int = 0,
        turn: int = 0,
        round: int = 0,
        player_init: Sequence[Player] = (),
    ):
        self.player_count = player_count
        self.turn = turn
        self.round = round
        self.start_player = start_player
        self.player_id = start_player
        player_dict = {player.player_id: player for player in player_init}
        # Use any players supplied, new players where not supplied
        self.players = [player_dict.get(player_id, Player(player_id)) for player_id in range(player_count)]

    def __repr__(self):
        return "\n".join(
            [
                f"Round: {self.round}, Turn: {self.turn}",
                "\n".join([player.__repr__() for player in self.players]),
                f"Game Scores: {[player.score for player in self.players]}",
            ]
        )

    def is_round_over(self) -> bool:
        return any([player.is_over() for player in self.players])

    def take_disc(self, player_id: int, target_id: int, disc_id) -> None:
        player = self.players[player_id]
        target = self.players[target_id]
        target.make_gone(disc_id)
        player.take(disc_id)

    def make_safe(self, target_id: int, disc_id: int) -> bool:
        return self.players[target_id].make_safe(disc_id)

    def make_vulnerable(self, target_id: int, disc_id: int) -> bool:
        return self.players[target_id].make_vulnerable(disc_id)

    def take_action(self, player_id: int, action: Action):
        print(f"Player: {player_id}: {action}")
        if action.new_state == DiscState.Gone:
            self.take_disc(player_id, action.target_id, action.disc_id)
        elif action.new_state == DiscState.Vulnerable:
            self.make_vulnerable(action.target_id, action.disc_id)
        elif action.new_state == DiscState.Safe:
            self.make_safe(action.target_id, action.disc_id)

    def winner_take_vulnerable_discs(self, winner_id: int):
        print(f"Giving vulnerable disks to winner: {winner_id}")
        for player_id, player in enumerate(self.players):
            if player_id != winner_id:
                for disc_id, disc in enumerate(player.discs):
                    if disc == DiscState.Vulnerable:
                        print(f"Taking {disc_id + 1} from {player_id}")
                        self.take_disc(winner_id, player_id, disc_id)

    def possible_actions(self, player_id: int, disc_id: int) -> Sequence[Action]:
        actions = []
        for target_id, target in enumerate(self.players):
            new_state = target.possible_new_state(disc_id, target_id == player_id)
            if new_state is not None:
                actions.append(Action(target_id, disc_id, new_state))
        return actions

    def play_turn(self, player_id: int, action: Action) -> bool:
        self.take_action(player_id, action)
        return self.is_round_over()

    def take_turn(self, player_id: int, strategy: Strategy) -> bool:
        dice = get_dice()
        for action in strategy.choose_actions(player_id, dice):
            self.play_turn(player_id, action)

        self.turn += 1

        return self.is_round_over()

    def end_round(self, winner_id: int) -> bool:
        self.winner_take_vulnerable_discs(winner_id)
        round_scores = [player.round_score for player in self.players]
        print(f"Scoring end of round: {round_scores}")

        scores = [player.end_round() for player in self.players]
        print(f"New score: {scores}")

        self.round += 1
        self.turn = 0
        return self.round >= self.player_count

    def set_initial_defence(self):
        for player_id in range(self.player_count):
            dice = get_unique_dice()
            for d in dice:
                self.play_turn(player_id, Action(player_id, d, DiscState.Safe))

    def winners(self) -> Sequence[int]:
        winning_score = max([player.score for player in self.players])
        return [player_idx for player_idx, player in enumerate(self.players) if player.score == winning_score]

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
