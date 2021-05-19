from typing import List, Optional

from game_implementation.disc_state import DiscState


class Player:
    def __init__(self):
        super(Player, self).__init__()
        self.taken: List[int] = []
        self.discs: List[DiscState] = [DiscState.Vulnerable] * 6
        self.score = 0
        self.reset()

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
        return sum(self.taken) + sum(
            [
                disc_id + 1
                for disc_id, disc in enumerate(self.discs)
                if disc == DiscState.Safe
            ]
        )

    @property
    def expected_score(self):
        return self.score + self.round_score

    def end_round(self):
        self.score += self.round_score
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

    def possible_new_state(self, disc_id: int, is_turn: bool) -> Optional[DiscState]:
        if is_turn:
            if self.discs[disc_id] == DiscState.Vulnerable:
                return DiscState.Safe
        else:
            if self.discs[disc_id] == DiscState.Safe:
                return DiscState.Vulnerable
            if self.discs[disc_id] == DiscState.Vulnerable:
                return DiscState.Gone
        return None
