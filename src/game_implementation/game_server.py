import random
from typing import Collection, Container, List, NamedTuple, Protocol

from game_implementation.action import Action
from game_implementation.dice import get_dice
from game_implementation.game import Game
from game_implementation.strategy_api import Strategy
from game_implementation.types import DiscId, PlayerCount, PlayerId


class ServerState(NamedTuple):
    game: Game
    turn_dice: Collection[DiscId]


CLIENT_PLAYER_ID = 0


class ServerApi(Protocol):
    def reset(self) -> None:
        """Start a new game"""
        pass

    def state(self) -> ServerState:
        """What is the current state of the game, including dice to play"""
        pass

    def act(self, target_id: PlayerId) -> bool:
        """
        Take an action using the current dice, play on until
        time for time to act with next dice or end of game.

        Args:
            target_id: player id (including 0 for self) to apply current dice to

        Returns:
            True if end of game
        """
        pass


class GameServer(ServerApi):
    """
    Runs game with a client making turn requests.

    Simple strategies are supplied for all players except the client.

    Examples:
        game_server = GameServer(3, strategies)

        game_server.reset()
        game_over = False
        while not game_over:
            dice_target = client.choose_action(game_server.game, game_server.current_dice)
            game_over = gave_server.play_dice(dice_target)
    """

    player_count: int
    """Number of players"""

    game: Game
    """The current game - replaced after a reset"""

    client_dice = List[DiscId]
    """
    The dice that the client has rolled.

    These will be played by the client in order and are removed after being played. Only the first dice is playable
    on the client's turn, and it is guaranteed to be legal to play.  To ensure this, dice will be removed before the
    client's turn if they are not legal to play. Consequently, if no dice in a roll are legal to play then all will
    be removed and the client's turn will be skipped. On the other hand dice afer the first are not removed until
    they become the first (i.e. previous dice have been removed by being played or removed as unplayable) so they can
    be seen, and so that the actions of earlier dice can, potentially, make them playable.
    """

    def __init__(self, player_count: PlayerCount, strategies: List[Strategy]):
        self.player_count = player_count
        # Player 0 (CLIENT_PLAYER_ID) is always the client, even though start_player is randomised
        assert len(strategies) == player_count - 1
        self.strategies = strategies

    def reset(self) -> None:
        self.game = Game(player_count=self.player_count, start_player=random.randint(0, self.player_count - 1))
        self.game.set_initial_defence()
        self._run_until_client_turn()

    def state(self) -> ServerState:
        return ServerState(self.game, self.client_dice)

    def _run_until_client_turn(self) -> bool:
        """
        Take other players' turns until game end or client's turn

        Returns:
            True if game end
        """
        while self.game.player_id != CLIENT_PLAYER_ID:
            end_of_round = self.game.take_turn(self.game.player_id, self.strategies[self.game.player_id - 1])
            if end_of_round:
                end_of_game = self.game.end_round(round_winner_id=self.game.player_id)
                if end_of_game:
                    return True
                self.game.next_player()

        return False

    @property
    def _current_die(self) -> DiscId:
        """Die for current player to play immediately"""
        return self.client_dice[0]

    def _roll_client_dice(self) -> None:
        """
        Roll a fresh set of dice for the client.
        Discard them until the first die is playable (or there are none left).
        """
        self.client_dice = list(get_dice())
        self._discard_first_client_die_while_unplayable()

    def _discard_first_client_die_while_unplayable(self) -> None:
        """
        Remove the first client die if it is unplayable; repeat until
        the first die is playable or the client has no more dice.
        """
        while len(self.client_dice) > 0:
            possible_actions = self.game.possible_actions(0, self.client_dice[0])
            if len(possible_actions) == 0:
                self.client_dice.pop(0)
            else:
                break

    def _next_client_die(self):
        """Discard the current (played) client die and dice after
        it that are unplayable."""
        self.client_dice.pop(0)
        self._discard_first_client_die_while_unplayable()

    def _make_action_for_target(self, target_id: PlayerId) -> Action:
        target_state = self.game.players[target_id].possible_new_state(self._current_die)
        assert target_state is not None
        return Action(target_id, self._current_die, target_state)

    def act(self, target_id: PlayerId) -> bool:
        """
        Use the current first dice. If it's the end of the client's turn then take
         other player's turns (and perform round ends) until it's the client's turn
          again or the game ends.

        Args:
            target_id: player id (self or other) to play the current dice against

        Returns:
            True if game is over, False if not
        """
        action = self._make_action_for_target(target_id)
        end_of_round = self.game.play_action(CLIENT_PLAYER_ID, action)
        if end_of_round:
            # does not need to wait for end of dice
            end_of_game = self.game.end_round(round_winner_id=CLIENT_PLAYER_ID)
            if end_of_game:
                return True
        else:
            self._next_client_die()

        while len(self.client_dice) == 0:
            self.game.next_player()
            end_of_game = self._run_until_client_turn()
            if end_of_game:
                return True
            else:
                self._roll_client_dice()

        return False
