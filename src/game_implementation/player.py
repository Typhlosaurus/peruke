from typing import Collection, Dict, List, Optional, Union

from game_implementation.disc_state import DiscState
from game_implementation.types import DiscId, DiscScore, PlayerId
from game_implementation.exceptions import DiscStateException


class Player:
    player_id: PlayerId
    """Id of player for reporting"""
    taken: List[DiscScore]
    """Scores of disks take (1..6)"""
    discs: List[DiscState]
    """6 Disc states"""
    score: int
    """Cumulative Score from previous rounds"""

    def __init__(
        self,
        player_id,
        init_taken: Collection[DiscScore] = (),
        init_score: int = 0,
        init_disks: Union[Collection[DiscState], Dict[DiscId, DiscState]] = (DiscState.Vulnerable,) * 6,
    ):
        self.player_id = player_id
        self.taken = [*init_taken]
        self.score = init_score

        if type(init_disks) is dict:
            discs = [DiscState.Vulnerable] * 6
            for disc_id, disc_state in init_disks.items():
                discs[disc_id] = disc_state
            print(discs)
        else:
            discs = [*init_disks]
        self.discs = discs

        if len(self.discs) != 6:
            raise ValueError(f"Illegal player disc set size: {len(self.discs)}")

    def __repr__(self) -> str:
        disc_state = ", ".join([disc.value for disc in self.discs])
        return f"{self.player_id}: {disc_state}. Taken={self.taken}. Round Score={self.round_score}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def reset(self):
        self.taken = []
        self.discs = [DiscState.Vulnerable] * 6

    def is_over(self) -> bool:
        return all(([disc == DiscState.Gone for disc in self.discs]))

    @property
    def round_score(self) -> int:
        """Putative additional score from current round if it ended now."""
        return sum(self.taken) + sum([disc_id + 1 for disc_id, disc in enumerate(self.discs) if disc == DiscState.Safe])

    @property
    def expected_score(self) -> int:
        """Putative score if current round ended now."""
        return self.score + self.round_score

    def end_round(self) -> int:
        """End current round now"""
        round_score = self.round_score
        print(f"Ending round for {self.player_id}: gaining {round_score}")
        self.score += round_score
        self.reset()
        return self.score

    def make_safe(self, disc_id: DiscId):
        if self.discs[disc_id] != DiscState.Vulnerable:
            raise DiscStateException(f"cannot make safe {self.discs[disc_id]}")
        self.discs[disc_id] = DiscState.Safe

    def make_vulnerable(self, disc_id: DiscId):
        if self.discs[disc_id] != DiscState.Safe:
            raise DiscStateException(f"cannot make vulnerable {self.discs[disc_id]}")
        self.discs[disc_id] = DiscState.Vulnerable

    def take(self, disc_id: DiscId):
        self.taken.append(disc_id + 1)

    def make_gone(self, disc_id: DiscId):
        if self.discs[disc_id] != DiscState.Vulnerable:
            raise DiscStateException(f"cannot take {self.discs[disc_id]}")
        self.discs[disc_id] = DiscState.Gone

    def possible_new_state(self, disc_id: DiscId, is_own_turn: bool) -> Optional[DiscState]:
        if is_own_turn:
            if self.discs[disc_id] == DiscState.Vulnerable:
                return DiscState.Safe
        else:
            if self.discs[disc_id] == DiscState.Safe:
                return DiscState.Vulnerable
            if self.discs[disc_id] == DiscState.Vulnerable:
                return DiscState.Gone
        return None
