from typing import NamedTuple

from game_implementation.disc_state import DiscState
from game_implementation.types import DiscId, PlayerId


class Action(NamedTuple):
    target_id: PlayerId
    disc_id: DiscId
    new_state: DiscState

    def __repr__(self):
        if self.new_state == DiscState.Gone:
            return f"Take {self.target_id}'s disk {self.disc_id + 1}"
        if self.new_state == DiscState.Vulnerable:
            return f"Make {self.target_id}'s disk {self.disc_id + 1} vulnerable"
        else:
            return f"Make my disk {self.disc_id + 1} safe"
