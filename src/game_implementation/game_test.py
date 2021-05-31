from typing import Dict, List, Sequence, Union

import pytest

from game_implementation.disc_state import DiscState
from game_implementation.exceptions import DiscStateException
from game_implementation.game import Game
from game_implementation.player import Player


class TestGame:
    @pytest.mark.parametrize(
        "player_states, expected_result",
        [
            ([Player(0, init_disks=[DiscState.Vulnerable] * 6)], False),
            ([Player(0, init_disks=[DiscState.Safe] * 6)], False),
            ([Player(0, init_disks=[DiscState.Gone] * 6)], True),
            ([Player(1, init_disks=[DiscState.Gone] * 6)], True),
            ([Player(2, init_disks=[DiscState.Gone] * 6)], True),
            ([Player(0, init_disks={3: DiscState.Safe})], False),
            ([Player(0, init_disks={3: DiscState.Gone})], False),
        ],
    )
    def test_is_round_over(self, player_states: List[Player], expected_result: bool):
        game = Game(player_count=3, start_player=0, turn=0, round=0, player_init=player_states)

        result = game.is_round_over()

        assert result == expected_result

    @pytest.mark.parametrize(
        "disk_id, initial_state, initial_taken, expected_taken",
        [(0, DiscState.Vulnerable, [], [1]), (5, DiscState.Vulnerable, [3], [3, 6]),],
    )
    def test_take_disc_success(
        self, disk_id: int, initial_state: DiscState, initial_taken: List[int], expected_taken: Union[bool, List[int]]
    ):

        game = Game(
            player_count=3,
            player_init=[Player(0, init_taken=initial_taken), Player(1, init_disks={disk_id: initial_state})],
        )

        game.take_disc(0, 1, disk_id)

        assert game.players[0] == Player(0, init_taken=expected_taken)
        assert game.players[1] == Player(1, init_disks={disk_id: DiscState.Gone})

    @pytest.mark.parametrize(
        "disk_id, initial_state", [(5, DiscState.Safe), (5, DiscState.Gone),],
    )
    def test_take_disc_fails(self, disk_id: int, initial_state: DiscState):

        game = Game(player_count=3, player_init=[Player(0), Player(1, init_disks={disk_id: initial_state})],)

        with pytest.raises(DiscStateException):
            game.take_disc(0, 1, disk_id)

    @pytest.mark.parametrize(
        "disc_id, initial_state", [(0, DiscState.Vulnerable), (5, DiscState.Vulnerable),],
    )
    def test_make_safe_success(self, disc_id: int, initial_state: DiscState):
        game = Game(player_count=3, player_init=[Player(1, init_disks={disc_id: initial_state})],)

        game.make_safe(1, disc_id)

        assert game.players[0] == Player(0)
        assert game.players[1] == Player(1, init_disks={disc_id: DiscState.Safe})
        assert game.players[2] == Player(2)

    @pytest.mark.parametrize(
        "disc_id, initial_state", [(0, DiscState.Gone), (5, DiscState.Gone), (0, DiscState.Safe), (5, DiscState.Safe),],
    )
    def test_make_safe_fails(self, disc_id: int, initial_state: DiscState):
        game = Game(player_count=3, player_init=[Player(1, init_disks={disc_id: initial_state})],)

        with pytest.raises(DiscStateException):
            game.make_safe(1, disc_id)

    @pytest.mark.parametrize(
        "disc_id, initial_state", [(0, DiscState.Safe), (5, DiscState.Safe),],
    )
    def test_make_vulnerable_success(self, disc_id: int, initial_state: DiscState):
        game = Game(player_count=3, player_init=[Player(1, init_disks={disc_id: initial_state})],)

        game.make_vulnerable(1, disc_id)

        assert game.players[0] == Player(0)
        assert game.players[1] == Player(1, init_disks={disc_id: DiscState.Vulnerable})
        assert game.players[2] == Player(2)

    @pytest.mark.parametrize(
        "disc_id, initial_state",
        [(0, DiscState.Gone), (5, DiscState.Gone), (0, DiscState.Vulnerable), (5, DiscState.Vulnerable),],
    )
    def test_make_vulnerable_fails(self, disc_id: int, initial_state: DiscState):
        game = Game(player_count=3, player_init=[Player(1, init_disks={disc_id: initial_state})],)

        with pytest.raises(DiscStateException):
            game.make_vulnerable(1, disc_id)
