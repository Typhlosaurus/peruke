from typing import List, Optional, Union

import pytest

from game_implementation.disc_state import DiscState
from game_implementation.exceptions import DiscStateException
from game_implementation.player import Player


class TestPlayer:
    def test_init(self):
        player = Player(0)

        assert player.discs == [
            DiscState.Vulnerable,
            DiscState.Vulnerable,
            DiscState.Vulnerable,
            DiscState.Vulnerable,
            DiscState.Vulnerable,
            DiscState.Vulnerable,
        ]
        assert player.score == 0
        assert player.taken == []
        assert player.round_score == 0

    def test_init_with_list_discs(self):
        player = Player(
            0, init_taken=[], init_score=0, init_disks=[DiscState.Vulnerable, DiscState.Safe, DiscState.Gone] * 2
        )

        assert player.discs == [
            DiscState.Vulnerable,
            DiscState.Safe,
            DiscState.Gone,
            DiscState.Vulnerable,
            DiscState.Safe,
            DiscState.Gone,
        ]
        assert player.score == 0
        assert player.taken == []
        assert player.round_score == 2 + 5

    def test_init_with_dict_discs(self):
        player = Player(
            0,
            init_taken=[],
            init_score=0,
            init_disks={1: DiscState.Safe, 2: DiscState.Gone, 4: DiscState.Safe, 5: DiscState.Gone},
        )

        assert player.discs == [
            DiscState.Vulnerable,
            DiscState.Safe,
            DiscState.Gone,
            DiscState.Vulnerable,
            DiscState.Safe,
            DiscState.Gone,
        ]
        assert player.score == 0
        assert player.taken == []
        assert player.round_score == 2 + 5

    def test_init_with_too_short_list(self):
        with pytest.raises(ValueError):
            Player(
                0, init_taken=[], init_score=0, init_disks=[],
            )

    def test_init_with_too_long_list(self):
        with pytest.raises(ValueError):
            Player(
                0, init_taken=[], init_score=0, init_disks=[DiscState.Vulnerable] * 7,
            )

    def test_init_with_bad_dict(self):
        with pytest.raises(IndexError):
            Player(
                0, init_taken=[], init_score=0, init_disks={6: DiscState.Safe},
            )

    def test_reset(self):
        player = Player(
            0, [3, 4], 1, [DiscState.Vulnerable, DiscState.Gone, DiscState.Safe] + [DiscState.Vulnerable] * 3
        )

        player.reset()

        assert player.discs == [
            DiscState.Vulnerable,
            DiscState.Vulnerable,
            DiscState.Vulnerable,
            DiscState.Vulnerable,
            DiscState.Vulnerable,
            DiscState.Vulnerable,
        ]
        assert player.taken == []
        assert player.round_score == 0
        assert player.score == 1  # No reset

    @pytest.mark.parametrize(
        "init_disks, is_over",
        [
            ([DiscState.Vulnerable] * 6, False,),
            ([DiscState.Safe] * 6, False,),
            ([DiscState.Gone] * 6, True,),
            ([DiscState.Gone] * 5 + [DiscState.Vulnerable], False,),
            ([DiscState.Vulnerable] + [DiscState.Gone] * 5, False,),
        ],
    )
    def test_is_over(self, init_disks, is_over):
        player = Player(0, [], 0, init_disks)

        assert player.is_over() == is_over

    @pytest.mark.parametrize(
        "disks, taken, expected_round_score",
        [
            [[DiscState.Vulnerable] * 6, [], 0],
            [[DiscState.Gone] * 6, [0], 0],
            [[DiscState.Vulnerable] * 6, [1, 3], 1 + 3],
            [[DiscState.Vulnerable] * 6, [1, 2, 3, 4, 5, 6], 1 + 2 + 3 + 4 + 5 + 6],
            [[DiscState.Vulnerable] * 3 + [DiscState.Safe] * 3, [0], 4 + 5 + 6],
            [[DiscState.Safe] + [DiscState.Gone] * 3 + [DiscState.Safe] * 2, [3], 1 + 5 + 6 + 3],
        ],
    )
    def test_round_score(self, disks: List[DiscState], taken: List[int], expected_round_score: int):
        player = Player(0, taken, 0, disks)

        assert player.round_score == expected_round_score

    @pytest.mark.parametrize(
        "disks, taken, current_score, expected_score",
        [
            [[DiscState.Vulnerable] * 6, [], 0, 0 + 0 + 0],
            [[DiscState.Gone] * 6, [0], 0, 0 + 0 + 0],
            [[DiscState.Safe] * 6, [0], 0, (1 + 2 + 3 + 4 + 5 + 6) + 0 + 0],
            [[DiscState.Vulnerable] * 6, [], 6, 0 + 0 + 6],
            [[DiscState.Gone] * 6, [], 6, 0 + 0 + 6],
            [[DiscState.Safe] * 6, [], 6, (1 + 2 + 3 + 4 + 5 + 6) + 0 + 6],
            [[DiscState.Vulnerable] * 6, [5, 6], 6, 0 + (5 + 6) + 6],
            [[DiscState.Gone] * 6, [5, 6], 6, 0 + (5 + 6) + 6],
            [[DiscState.Safe] * 6, [5, 6], 6, ((1 + 2 + 3 + 4 + 5 + 6) + (5 + 6) + 6)],
            [
                [DiscState.Gone] * 2 + [DiscState.Safe] * 2 + [DiscState.Vulnerable] * 2,
                [1, 3],
                5,
                (3 + 4) + (1 + 3) + 5,
            ],
        ],
    )
    def test_end_round(self, disks: List[DiscState], taken: List[int], current_score: int, expected_score: int):
        player = Player(0, taken, current_score, disks)

        player.end_round()

        assert player.score == expected_score

    @pytest.mark.parametrize(
        "disks, safe_disk_id, expected_disks",
        [
            ([DiscState.Vulnerable] * 6, 0, [DiscState.Safe] + [DiscState.Vulnerable] * 5),
            ([DiscState.Vulnerable] * 6, 1, [DiscState.Vulnerable, DiscState.Safe] + [DiscState.Vulnerable] * 4),
            ([DiscState.Vulnerable] * 6, 5, [DiscState.Vulnerable] * 5 + [DiscState.Safe]),
            ([DiscState.Safe] * 6, 1, False),
            ([DiscState.Gone] * 6, 1, False),
        ],
    )
    def test_make_safe(self, disks: List[DiscState], safe_disk_id: int, expected_disks: Union[bool, List[DiscState]]):
        player = Player(0, [], 0, disks)

        if expected_disks:
            player.make_safe(safe_disk_id)
            assert player.discs == expected_disks
        else:
            with pytest.raises(DiscStateException, match=f"cannot make safe {player.discs[safe_disk_id]}"):
                player.make_safe(safe_disk_id)

    @pytest.mark.parametrize(
        "disks, safe_disk_id, expected_disks",
        [
            ([DiscState.Safe] * 6, 0, [DiscState.Vulnerable] + [DiscState.Safe] * 5),
            ([DiscState.Safe] * 6, 1, [DiscState.Safe, DiscState.Vulnerable] + [DiscState.Safe] * 4),
            ([DiscState.Safe] * 6, 5, [DiscState.Safe] * 5 + [DiscState.Vulnerable]),
            ([DiscState.Vulnerable] * 6, 1, False),
            ([DiscState.Gone] * 6, 1, False),
        ],
    )
    def test_make_vulnerable(
        self, disks: List[DiscState], safe_disk_id: int, expected_disks: Union[bool, List[DiscState]]
    ):
        player = Player(0, [], 0, disks)

        if expected_disks:
            player.make_vulnerable(safe_disk_id)
            assert player.discs == expected_disks
        else:
            with pytest.raises(DiscStateException, match=f"cannot make vulnerable {player.discs[safe_disk_id]}"):
                player.make_vulnerable(safe_disk_id)

    @pytest.mark.parametrize(
        "disks, safe_disk_id, expected_disks",
        [
            ([DiscState.Vulnerable] * 6, 0, [DiscState.Gone] + [DiscState.Vulnerable] * 5),
            ([DiscState.Vulnerable] * 6, 1, [DiscState.Vulnerable, DiscState.Gone] + [DiscState.Vulnerable] * 4),
            ([DiscState.Vulnerable] * 6, 5, [DiscState.Vulnerable] * 5 + [DiscState.Gone]),
            ([DiscState.Safe] * 6, 1, False),
            ([DiscState.Gone] * 6, 1, False),
        ],
    )
    def test_make_gone(self, disks: List[DiscState], safe_disk_id: int, expected_disks: Union[bool, List[DiscState]]):
        player = Player(0, [], 0, disks)

        if expected_disks:
            player.make_gone(safe_disk_id)
            assert player.discs == expected_disks
        else:
            with pytest.raises(DiscStateException, match=f"cannot take {player.discs[safe_disk_id]}"):
                player.make_gone(safe_disk_id)

    @pytest.mark.parametrize("disc_id", [0, 5])
    def test_take(self, disc_id):
        player = Player(0)

        player.take(disc_id)

        assert player.round_score == disc_id + 1

    @pytest.mark.parametrize(
        "disks, disk_id, is_own_turn, expected_state",
        [
            ([DiscState.Safe] * 2 + [DiscState.Vulnerable] + [DiscState.Safe] * 3, 2, False, DiscState.Gone),
            ([DiscState.Gone] * 2 + [DiscState.Safe] + [DiscState.Gone] * 3, 2, False, DiscState.Vulnerable,),
            ([DiscState.Safe] * 2 + [DiscState.Gone] + [DiscState.Safe] * 3, 2, False, None),
            ([DiscState.Safe] * 2 + [DiscState.Vulnerable] + [DiscState.Safe] * 3, 2, True, DiscState.Safe),
            ([DiscState.Vulnerable] * 2 + [DiscState.Safe] + [DiscState.Vulnerable] * 3, 2, True, None),
            ([DiscState.Vulnerable] * 2 + [DiscState.Gone] + [DiscState.Vulnerable] * 3, 2, True, None),
        ],
    )
    def test_possible_new_state(
        self, disks: List[DiscState], disk_id: int, is_own_turn: bool, expected_state: Optional[DiscState]
    ):
        player = Player(0, init_disks=disks)

        new_state = player.possible_new_state(disk_id, is_own_turn)

        assert new_state == expected_state
