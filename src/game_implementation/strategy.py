import random
from abc import ABC
from typing import Any, Collection, Dict, Tuple

from game_implementation.action import Action
from game_implementation.disc_state import DiscState
from game_implementation.game import Game
from game_implementation.strategy_api import Strategy
from game_implementation.types import DiscId, PlayerId


class RandomStrategy(Strategy):
    def choose_actions(self, game: Game, player_id: PlayerId, dice: Collection[DiscId]) -> Collection[Action]:
        for d in dice:
            possible_actions = game.possible_actions(player_id, d)
            if len(possible_actions) > 0:
                yield random.choice(possible_actions)


class SimpleSortedStrategy(Strategy, ABC):
    def ordering(self, game: Game, action: Action) -> Any:
        raise NotImplementedError()

    def choose_actions(self, game: Game, player_id: PlayerId, dice: Collection[DiscId]) -> Collection[Action]:
        for d in dice:
            possible_actions = game.possible_actions(player_id, d)
            if len(possible_actions) > 0:
                ordered = sorted(possible_actions, key=lambda action: self.ordering(game, action))
                yield ordered[-1]


class TallestDaisyStrategy(SimpleSortedStrategy):
    def __init__(self, action_preference: Dict[DiscState, int]):
        self.action_preference = action_preference

    def ordering(self, game: Game, action: Action):
        # prefer first by action type, then by highest score
        return (
            self.action_preference[action.new_state],
            -game.players[action.target_id].expected_score,
        )


class PreferTakeOnDoubleSafeDie(Strategy):
    def __init__(self, action_preference: Dict[Tuple[DiscState, bool], int]):
        self.action_preference = action_preference

    def ordering(self, game: Game, action: Action, same_die_available: bool):
        # prefer first by action type and extra copies of dice available, then by highest score
        return (
            self.action_preference[(action.new_state, same_die_available)],
            -game.players[action.target_id].expected_score,
        )

    def choose_actions(self, game: Game, player_id: PlayerId, dice: Collection[DiscId]) -> Collection[Action]:
        remaining_dice = list(dice)
        while len(remaining_dice) > 0:
            die = remaining_dice.pop()
            possible_actions = game.possible_actions(player_id, die)
            if len(possible_actions) > 0:
                ordered = sorted(
                    possible_actions, key=lambda action: self.ordering(game, action, die in remaining_dice)
                )
                yield ordered[-1]
