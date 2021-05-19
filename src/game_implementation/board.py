from collections import Sequence

from game_implementation.action import Action
from game_implementation.disc_state import DiscState
from game_implementation.player import Player


class Board:
    def __init__(self, player_count: int):
        self.players = [Player() for _ in range(player_count)]

    def __repr__(self) -> str:
        return "\n".join([player.__repr__() for player in self.players])

    def reset(self):
        for player in self.players:
            player.reset()

    def is_round_over(self) -> bool:
        return any([player.is_over() for player in self.players])

    def take_disc(self, player_id: int, target_id: int, disc_id):
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

    def take_for_round_winner(self, winner_id: int):
        print(f"Giving vulnerable disks to winner: {winner_id}")
        for player_id, player in enumerate(self.players):
            if player_id != winner_id:
                for disc_id, disc in enumerate(player.discs):
                    if disc == DiscState.Vulnerable:
                        print(f"Taking {disc_id + 1} from {player_id}")
                        self.take_disc(winner_id, player_id, disc_id)

    def score_round(self, winner_id: int) -> Sequence[int]:
        self.take_for_round_winner(winner_id)
        round_scores = [player.round_score for player in self.players]
        print(f"Scoring end of round: {round_scores}")

        scores = [player.end_round() for player in self.players]
        print(f"New score: {scores}")

        return scores

    def possible_actions(self, player_id: int, disc_id: int) -> Sequence[Action]:
        actions = []
        for target_id, target in enumerate(self.players):
            new_state = target.possible_new_state(disc_id, target_id == player_id)
            if new_state is not None:
                actions.append(Action(target_id, disc_id, new_state))
        return actions
