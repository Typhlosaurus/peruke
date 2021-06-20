from __future__ import annotations

from typing import Collection, Protocol, TYPE_CHECKING

from game_implementation.action import Action
from game_implementation.game_types import DiscId, PlayerId

if TYPE_CHECKING:
    from game import Game


class Strategy(Protocol):
    def choose_actions(self, game: Game, player_id: PlayerId, dice: Collection[DiscId]) -> Collection[Action]:
        pass
