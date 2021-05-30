from typing import List, Optional, Sequence

from game_implementation.disc_state import DiscState


class Player:
    player_id: int
    """Id of player for reporting"""
    taken: List[int]
    """Scores of disks take (1..6)"""
    discs: List[DiscState]
    """6 Disc states"""
    score: int
    """Cumulative Score from previous rounds"""

    def __init__(
        self,
        player_id,
        init_disks: Sequence[DiscState] = (DiscState.Vulnerable,) * 6,
        init_taken: Sequence[int] = (),
        init_score: int = 0,
    ):
        self.player_id = player_id
        self.discs = [*init_disks]
        assert len(init_disks) == 6
        self.taken = [*init_taken]
        self.score = init_score

    def __repr__(self) -> str:
        disc_state = ", ".join([disc.value for disc in self.discs])
        return f"{disc_state}. Taken={self.taken}. Round Score={self.round_score}"

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
    def expected_score(self):
        """Putative score if current round ended now."""
        return self.score + self.round_score

    def end_round(self):
        """End current round now"""
        round_score = self.round_score
        print(f"Ending round for {self.player_id}: gaining {round_score}")
        self.score += round_score
        self.reset()
        return self.score

    def make_safe(self, disc_id: int):
        if self.discs[disc_id] != DiscState.Vulnerable:
            raise Exception(f"cannot make safe {self.discs[disc_id]}")
        self.discs[disc_id] = DiscState.Safe

    def make_vulnerable(self, disc_id: int):
        if self.discs[disc_id] != DiscState.Safe:
            raise Exception(f"cannot make vulnerable {self.discs[disc_id]}")
        self.discs[disc_id] = DiscState.Vulnerable

    def take(self, disc_id: int):
        self.taken.append(disc_id + 1)

    def make_gone(self, disc_id: int):
        if self.discs[disc_id] != DiscState.Vulnerable:
            raise Exception(f"cannot take {self.discs[disc_id]}")
        self.discs[disc_id] = DiscState.Gone

    def possible_new_state(self, disc_id: int, is_own_turn: bool) -> Optional[DiscState]:
        if is_own_turn:
            if self.discs[disc_id] == DiscState.Vulnerable:
                return DiscState.Safe
        else:
            if self.discs[disc_id] == DiscState.Safe:
                return DiscState.Vulnerable
            if self.discs[disc_id] == DiscState.Vulnerable:
                return DiscState.Gone
        return None
