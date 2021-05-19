import random
from abc import ABC
from typing import Any, Dict, Sequence

from game_implementation.action import Action
from game_implementation.disc_state import DiscState
from game_implementation.game import Game, Strategy


class RandomStrategy(Strategy):
    def __init__(self, game: Game):
        self.game = game

    def choose_actions(self, player_id: int, dice: Sequence[int]) -> Sequence[Action]:
        for d in dice:
            possible_actions = self.game.board.possible_actions(player_id, d)
            if len(possible_actions) > 0:
                yield random.choice(possible_actions)


class SimpleSortedStrategy(Strategy, ABC):
    def __init__(self, game: Game):
        self.game = game

    def ordering(self, action: Action) -> Any:
        raise NotImplemented()

    def choose_actions(self, player_id: int, dice: Sequence[int]) -> Sequence[Action]:
        for d in dice:
            possible_actions = self.game.board.possible_actions(player_id, d)
            if len(possible_actions) > 0:
                ordered = sorted(possible_actions, key=self.ordering)
                yield ordered[-1]


class TallestDaisyStrategy(SimpleSortedStrategy):
    def __init__(self, game: Game, action_preference: Dict[DiscState, int]):
        super().__init__(game)
        self.action_preference = action_preference

    def ordering(self, action: Action):
        # prefer first by action type, then by highest score
        return (
            self.action_preference[action.new_state],
            self.game.board.players[action.target_id].expected_score,
        )
