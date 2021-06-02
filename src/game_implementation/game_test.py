from typing import Dict, List, Sequence, Union

import pytest
from pytest_mock import MockFixture

from game_implementation.action import Action
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
        [(0, DiscState.Vulnerable, [], [1]), (5, DiscState.Vulnerable, [3], [3, 6])],
    )
    def test_take_disc_success(
        self, disk_id: int, initial_state: DiscState, initial_taken: List[int], expected_taken: Union[bool, List[int]]
    ):

        game = Game(
            player_count=3,
            player_init=[Player(0, init_taken=initial_taken), Player(1, init_disks={disk_id: initial_state})],
        )

        game.take_disc(game.players[0], game.players[1], disk_id)

        assert game.players[0] == Player(0, init_taken=expected_taken)
        assert game.players[1] == Player(1, init_disks={disk_id: DiscState.Gone})

    @pytest.mark.parametrize(
        "disk_id, initial_state", [(5, DiscState.Safe), (5, DiscState.Gone)],
    )
    def test_take_disc_fails(self, disk_id: int, initial_state: DiscState):

        game = Game(player_count=3, player_init=[Player(0), Player(1, init_disks={disk_id: initial_state})],)

        with pytest.raises(DiscStateException):
            game.take_disc(game.players[0], game.players[1], disk_id)

    @pytest.mark.parametrize(
        "player0, player1, action, expected_player0, expected_player1",
        [
            (
                Player(0, init_disks={1: DiscState.Gone}),
                Player(1),
                Action(target_id=0, disc_id=0, new_state=DiscState.Safe),
                Player(0, init_disks={0: DiscState.Safe, 1: DiscState.Gone}),
                Player(1),
            ),
            (
                Player(0, init_disks={4: DiscState.Gone}, init_taken=[1]),
                Player(1, init_taken=[2]),
                Action(target_id=0, disc_id=5, new_state=DiscState.Safe),
                Player(0, init_disks={4: DiscState.Gone, 5: DiscState.Safe}, init_taken=[1]),
                Player(1, init_taken=[2]),
            ),
            (
                Player(0),
                Player(1, init_disks={0: DiscState.Safe}),
                Action(target_id=1, disc_id=0, new_state=DiscState.Vulnerable),
                Player(0),
                Player(1),
            ),
            (
                Player(0, init_taken=[1]),
                Player(1, init_disks={5: DiscState.Safe}, init_taken=[2]),
                Action(target_id=1, disc_id=5, new_state=DiscState.Vulnerable),
                Player(0, init_taken=[1]),
                Player(1, init_taken=[2]),
            ),
            (
                Player(0),
                Player(1, init_disks={1: DiscState.Gone}),
                Action(target_id=1, disc_id=0, new_state=DiscState.Gone),
                Player(0, init_taken=[1]),
                Player(1, init_disks={0: DiscState.Gone, 1: DiscState.Gone}),
            ),
            (
                Player(0, init_taken=[1]),
                Player(1, init_disks={4: DiscState.Gone}, init_taken=[2]),
                Action(target_id=1, disc_id=5, new_state=DiscState.Gone),
                Player(0, init_taken=[1, 6]),
                Player(1, init_disks={4: DiscState.Gone, 5: DiscState.Gone}, init_taken=[2]),
            ),
        ],
    )
    def test_play_action_succeeds(
        self, player0: Player, player1: Player, action: Action, expected_player0: Player, expected_player1: Player
    ):
        game = Game(player_count=2, player_init=[player0, player1])

        game.play_action(0, action)

        assert game.players == [expected_player0, expected_player1]

    @pytest.mark.parametrize(
        "player0, player1, action",
        [
            (
                Player(0, init_disks={1: DiscState.Safe}),
                Player(1),
                Action(target_id=0, disc_id=1, new_state=DiscState.Safe),
            ),
            (
                Player(0, init_disks={4: DiscState.Gone}),
                Player(1),
                Action(target_id=0, disc_id=4, new_state=DiscState.Safe),
            ),
            (
                Player(0),
                Player(1, init_disks={0: DiscState.Vulnerable}),
                Action(target_id=1, disc_id=0, new_state=DiscState.Vulnerable),
            ),
            (
                Player(0),
                Player(1, init_disks={5: DiscState.Gone}),
                Action(target_id=1, disc_id=5, new_state=DiscState.Vulnerable),
            ),
            (
                Player(0),
                Player(1, init_disks={0: DiscState.Gone}),
                Action(target_id=1, disc_id=0, new_state=DiscState.Gone),
            ),
            (
                Player(0),
                Player(1, init_disks={5: DiscState.Safe}),
                Action(target_id=1, disc_id=5, new_state=DiscState.Gone),
            ),
        ],
    )
    def test_play_action_fails(self, player0: Player, player1: Player, action: Action):
        game = Game(player_count=3, player_init=[player0, player1])
        with pytest.raises(DiscStateException):
            game.play_action(0, action)

    @pytest.mark.parametrize(
        "player0, player1, player2, expected_player0, expected_player1, expected_player2",
        [
            (
                Player(0),
                Player(1),
                Player(2),
                Player(0, init_disks=[DiscState.Gone] * 6),
                Player(1, init_taken=[*range(1, 7)] * 2),
                Player(2, init_disks=[DiscState.Gone] * 6),
            ),
            (
                Player(0, init_disks=[DiscState.Gone] * 5 + [DiscState.Vulnerable], init_taken=[1]),
                Player(1),
                Player(2, init_disks=[DiscState.Safe] * 5 + [DiscState.Vulnerable], init_taken=[2]),
                Player(0),
                Player(1),
                Player(2),
            ),
        ],
    )
    def test_winner_take_vulnerable_discs(
        self,
        player0: Player,
        player1: Player,
        player2: Player,
        expected_player0: Player,
        expected_player1: Player,
        expected_player2: Player,
    ):
        game = Game(player_count=3, player_init=[player0, player1, player2])

        game.winner_take_vulnerable_discs(winner_id=1)

        assert game.players == [expected_player0, expected_player1, expected_player2]

    def test_possible_actions(self):
        game = Game(player_count=3, player_init=[])

        game.possible_actions()
        assert False

    def test_play_turn(self):
        game = Game(player_count=3, player_init=[])

        game.play_action()
        assert False

    def test_take_turn(self):
        game = Game(player_count=3, player_init=[])

        game.take_turn()
        assert False

    def test_end_round(self):
        game = Game(player_count=3, player_init=[])

        game.end_round()
        assert False

    def test_set_initial_defence(self, mocker: MockFixture):
        mocker.patch("game_implementation.game.get_unique_dice", return_value={1, 2, 3})

        game = Game(player_count=3, player_init=[])
        game.set_initial_defence()

        assert game.players[0] == Player(0, init_disks={1: DiscState.Safe, 2: DiscState.Safe, 3: DiscState.Safe,})
        assert game.players[1] == Player(0, init_disks={1: DiscState.Safe, 2: DiscState.Safe, 3: DiscState.Safe,})
        assert game.players[2] == Player(0, init_disks={1: DiscState.Safe, 2: DiscState.Safe, 3: DiscState.Safe,})

    def test_winners(self):
        game = Game(player_count=3, player_init=[])

        game.winners()
        assert False

    def test_play(self):
        game = Game(player_count=3, player_init=[])

        game.play()
        assert False
