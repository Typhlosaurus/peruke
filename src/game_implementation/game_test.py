from typing import Collection, List, Union

# from unittest.mock import MagicMock
from unittest.mock import call, MagicMock

import pytest
from pytest_mock import MockFixture

from game_implementation.action import Action
from game_implementation.disc_state import DiscState
from game_implementation.exceptions import DiscStateException, IllegalMoveException
from game_implementation.game import Game, Strategy
from game_implementation.player import Player
from game_implementation.game_types import DiscId, PlayerId


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
                Player(0, init_disks=[DiscState.Gone] * 6, init_taken=[1]),
                Player(1, init_taken=[6, 6]),
                Player(2, init_disks=[DiscState.Safe] * 5 + [DiscState.Gone], init_taken=[2]),
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

    @pytest.mark.parametrize(
        "player0, player1, dice, expected_actions",
        [
            (
                Player(0, init_disks={0: DiscState.Vulnerable}),
                Player(1, init_disks={0: DiscState.Vulnerable}),
                0,
                [Action(0, 0, DiscState.Safe), Action(1, 0, DiscState.Gone)],
            ),
            (Player(0, init_disks={0: DiscState.Safe}), Player(1, init_disks={0: DiscState.Gone}), 0, []),
            (
                Player(0, init_disks={0: DiscState.Gone}),
                Player(1, init_disks={0: DiscState.Safe}),
                0,
                [Action(1, 0, DiscState.Vulnerable)],
            ),
            (
                Player(0, init_disks={4: DiscState.Vulnerable}),
                Player(1, init_disks={4: DiscState.Safe}),
                4,
                [Action(0, 4, DiscState.Safe), Action(1, 4, DiscState.Vulnerable)],
            ),
        ],
    )
    def test_possible_actions(self, player0: Player, player1: Player, dice: DiscId, expected_actions: List[Action]):
        game = Game(player_count=2, player_init=[player0, player1])

        possible_actions = game.possible_actions(0, dice)

        assert possible_actions == expected_actions

    @pytest.mark.parametrize(
        "init_players, dice_rolls, chosen_actions, expected_player_states",
        [
            (
                # all different dice, all used
                [Player(0), Player(1)],
                [1, 2, 3],
                [Action(0, 1, DiscState.Safe), Action(1, 2, DiscState.Gone), Action(1, 3, DiscState.Gone)],
                [
                    Player(0, init_disks={1: DiscState.Safe}, init_taken=[3, 4]),
                    Player(1, init_disks={2: DiscState.Gone, 3: DiscState.Gone}),
                ],
            ),
            (
                # Duplicate dice and an unusable dice
                [
                    Player(0, init_disks={1: DiscState.Gone}),
                    Player(1, init_disks={1: DiscState.Gone, 2: DiscState.Safe}),
                ],
                [1, 2, 2],
                [Action(1, 2, DiscState.Vulnerable), Action(1, 2, DiscState.Gone)],
                [
                    Player(0, init_disks={1: DiscState.Gone}, init_taken=[3]),
                    Player(1, init_disks={1: DiscState.Gone, 2: DiscState.Gone}),
                ],
            ),
            (
                # Unusable duplicate dice
                [Player(0), Player(1)],
                [2, 2, 2],
                [Action(0, 2, DiscState.Safe), Action(1, 2, DiscState.Gone)],
                [Player(0, init_disks={2: DiscState.Safe}, init_taken=[3]), Player(1, init_disks={2: DiscState.Gone})],
            ),
        ],
    )
    def test_take_turn_succeeds(
        self,
        mocker: MockFixture,
        init_players: Collection[Player],
        dice_rolls: Collection[DiscId],
        chosen_actions: Collection[Action],
        expected_player_states: Collection[Player],
    ):
        class TestStrategy(Strategy):
            def choose_actions(self, game: Game, player_id: PlayerId, dice: Collection[DiscId]) -> Collection[Action]:
                assert dice == dice_rolls
                return chosen_actions

        strategy = TestStrategy()
        mocker.patch("game_implementation.game.get_dice", return_value=dice_rolls)
        test_game = Game(player_count=2, player_init=init_players)

        test_game.take_turn(0, strategy)

        assert test_game.players == expected_player_states

    @pytest.mark.parametrize(
        "init_players, dice_rolls, chosen_actions",
        [
            (
                # Unused dice
                [Player(0), Player(1)],
                [1, 2, 3],
                [Action(0, 1, DiscState.Safe), Action(1, 2, DiscState.Gone)],
            ),
            (
                # Unused duplicate dice
                [
                    Player(0, init_disks={1: DiscState.Gone}),
                    Player(1, init_disks={1: DiscState.Gone, 2: DiscState.Safe}),
                ],
                [1, 2, 2],
                [Action(1, 2, DiscState.Vulnerable)],
            ),
            (
                # dice used twice
                [Player(0), Player(1)],
                [1, 2, 3],
                [
                    Action(0, 1, DiscState.Safe),
                    Action(1, 2, DiscState.Gone),
                    Action(1, 3, DiscState.Gone),
                    Action(1, 3, DiscState.Gone),
                ],
            ),
        ],
    )
    def test_take_turn_fails(
        self,
        mocker: MockFixture,
        init_players: Collection[Player],
        dice_rolls: Collection[DiscId],
        chosen_actions: Collection[Action],
    ):
        class TestStrategy(Strategy):
            def choose_actions(self, game, player_id: PlayerId, dice: Collection[DiscId]) -> Collection[Action]:
                assert dice == dice_rolls
                return chosen_actions

        strategy = TestStrategy()
        mocker.patch("game_implementation.game.get_dice", return_value=dice_rolls)
        game = Game(player_count=2, player_init=init_players)

        with pytest.raises(IllegalMoveException):
            game.take_turn(0, strategy)

    @pytest.mark.parametrize(
        "round_ending, init_players, final_scores, expected_game_end",
        [
            # Take all disks
            (0, [Player(0), Player(1), Player(2)], [0, sum(range(1, 7)) * 2, 0], False),
            # all disks safe - score all safe disks, take no disks
            (
                1,
                [
                    Player(0, init_disks=[DiscState.Safe] * 6),
                    Player(1, init_disks=[DiscState.Safe] * 6),
                    Player(2, init_disks=[DiscState.Safe] * 6),
                ],
                [sum(range(1, 7))] * 3,
                False,
            ),
            # Take all disks except 1 safe per player, add to initial scores
            (
                2,
                [
                    Player(0, init_score=10, init_disks={5: DiscState.Safe}),
                    Player(1, init_score=11, init_disks={5: DiscState.Safe}),
                    Player(2, init_score=12, init_disks={5: DiscState.Safe}),
                ],
                [10 + 6, 11 + 6 + sum(range(1, 6)) * 2, 12 + 6],
                True,
            ),
        ],
    )
    def test_end_round_given_winner_is_1(
        self,
        round_ending: PlayerId,
        init_players: List[Player],
        final_scores: List[int],
        expected_game_end: bool,
        mocker: MockFixture,
    ):
        game = Game(player_count=3, player_init=init_players, round=round_ending)
        mock_set_initial_defence = mocker.patch.object(game, "set_initial_defence")

        game_end = game.end_round(1)

        assert game_end == expected_game_end
        assert final_scores == [player.score for player in game.players]
        if game_end:
            mock_set_initial_defence.assert_not_called()
        else:
            mock_set_initial_defence.assert_called_once()

    def test_set_initial_defence(self, mocker: MockFixture):
        mocker.patch("game_implementation.game.get_unique_dice", side_effect=[{1, 2, 3}, {2, 3}, {4, 5, 3}])

        game = Game(player_count=3, player_init=[])
        game.set_initial_defence()

        assert game.players[0] == Player(0, init_disks={1: DiscState.Safe, 2: DiscState.Safe, 3: DiscState.Safe})
        assert game.players[1] == Player(1, init_disks={2: DiscState.Safe, 3: DiscState.Safe})
        assert game.players[2] == Player(2, init_disks={3: DiscState.Safe, 4: DiscState.Safe, 5: DiscState.Safe})

    @pytest.mark.parametrize("player_id, expected_next_player_id", [(0, 1), (1, 2), (2, 0)])
    def test_next_player(self, player_id: PlayerId, expected_next_player_id: PlayerId):
        game = Game(player_count=3)
        game.player_id = player_id
        game.next_player()

        assert game.player_id == expected_next_player_id

    def test_winners(self):
        game = Game(
            player_count=3, player_init=[Player(0, init_score=20), Player(1, init_score=18), Player(2, init_score=20)]
        )

        assert game.winners() == [0, 2]

    def test_play_round(self, mocker: MockFixture):
        game = Game(player_count=3, player_init=[])

        mock_take_turn = mocker.patch.object(game, "take_turn", side_effect=[False, False, False, True])
        mock_end_round = mocker.patch.object(game, "end_round", side_effect=[True])
        mock_strategy = MagicMock(Strategy)
        strategies = [mock_strategy] * 3

        end_game = game.play_round(strategies)

        assert mock_take_turn.call_count == 4
        print(mock_take_turn.mock_calls)
        mock_take_turn.assert_has_calls(
            [call(0, mock_strategy), call(1, mock_strategy), call(2, mock_strategy), call(0, mock_strategy)]
        )
        mock_end_round.assert_called_once_with(round_winner_id=0)
        assert game.player_id == 1
        assert end_game is True

    def test_play(self, mocker: MockFixture):
        game = Game(player_count=3, player_init=[])

        mock_set_initial_defence = mocker.patch.object(game, "set_initial_defence")
        mock_play_round = mocker.patch.object(game, "play_round", side_effect=[False, False, True])
        mocker.patch.object(game, "winners", side_effect=[[3, 2]])

        mock_strategy = MagicMock(Strategy)
        strategies = [mock_strategy] * 3

        winners = game.play(strategies)

        assert mock_set_initial_defence.call_count == 1
        assert mock_play_round.call_count == 3
        assert winners == [3, 2]
