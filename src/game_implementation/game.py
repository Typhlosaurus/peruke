from typing import Collection, List, Literal, Protocol, Sequence

from game_implementation.action import Action
from game_implementation.dice import get_dice, get_unique_dice
from game_implementation.disc_state import DiscState
from game_implementation.exceptions import IllegalMoveException
from game_implementation.player import Player
from game_implementation.types import DiscId, PlayerId


class Strategy(Protocol):
    def choose_actions(self, player_id: PlayerId, dice: Collection[DiscId]) -> Collection[Action]:
        pass


class Game:
    player_count: Literal[2, 3, 4]
    start_player: PlayerId
    turn: int
    round: PlayerId
    players: List[Player]

    def __init__(
        self,
        player_count: Literal[2, 3, 4] = 3,
        start_player: PlayerId = 0,
        turn: int = 0,
        round: PlayerId = 0,
        player_init: Collection[Player] = (),
    ):
        self.player_count = player_count
        self.turn = turn
        self.round = round
        self.start_player = start_player
        self.player_id = start_player
        player_dict = {player.player_id: player for player in player_init}
        # Use any players supplied, create new players where not supplied
        self.players = [player_dict.get(player_id, Player(player_id)) for player_id in range(player_count)]

    def __repr__(self):
        return "\n".join(
            [
                f"Round: {self.round}, Turn: {self.turn}",
                "\n".join([player.__repr__() for player in self.players]),
                f"Game Scores: {[player.score for player in self.players]}",
            ]
        )

    def is_round_over(self) -> bool:
        return any([player.is_over() for player in self.players])

    def take_disc(self, taker: Player, target: Player, disc_id: DiscId) -> None:
        target.make_gone(disc_id)
        taker.take(disc_id)

    def winner_take_vulnerable_discs(self, winner_id: PlayerId):
        print(f"Giving vulnerable disks to winner: {winner_id}")
        winner = self.players[winner_id]
        loosers = [looser for looser in self.players if looser.player_id != winner_id]
        for looser in loosers:
            disc_ids = [disc_id for disc_id, disc in enumerate(looser.discs) if disc == DiscState.Vulnerable]
            for disc_id in disc_ids:
                print(f"Taking {disc_id + 1} from {looser.player_id}")
                self.take_disc(winner, looser, disc_id)

    def play_action(self, player_id: PlayerId, action: Action) -> bool:
        print(f"Player: {player_id}: {action}")
        target = self.players[action.target_id]
        if action.new_state == DiscState.Gone:
            player = self.players[player_id]
            self.take_disc(player, target, action.disc_id)
        elif action.new_state == DiscState.Vulnerable:
            target.make_vulnerable(action.disc_id)
        elif action.new_state == DiscState.Safe:
            target.make_safe(action.disc_id)

        return self.is_round_over()

    def possible_actions(self, player_id: PlayerId, disc_id: DiscId) -> Sequence[Action]:
        actions = []
        for target in self.players:
            new_state = target.possible_new_state(disc_id, target.player_id == player_id)
            if new_state is not None:
                actions.append(Action(target.player_id, disc_id, new_state))
        return actions

    def take_turn(self, player_id: PlayerId, strategy: Strategy) -> bool:
        """
        Roll dice for a player, choose and take actions.

        Args:
            player_id: id of player
            strategy: used to choose actions

        Returns:
            True if round is over
        """
        dice = get_dice()
        remaining_dice = [*dice]

        for action in strategy.choose_actions(player_id, dice):
            if action.disc_id not in remaining_dice:
                if action.disc_id in dice:
                    raise IllegalMoveException(f"Dice {action.disc_id} already used ({action})")
                else:
                    raise IllegalMoveException(f"Dice {action.disc_id} was not rolled ({action})")
            self.play_action(player_id, action)
            remaining_dice.remove(action.disc_id)

        for unused_dice in remaining_dice:
            available_action = [*self.possible_actions(player_id, unused_dice)]
            if len(available_action):
                raise IllegalMoveException(f"Unused dice {unused_dice}")
        self.turn += 1

        return self.is_round_over()

    def end_round(self, winner_id: PlayerId) -> bool:
        """
        Winner takes vulnerable disks; update all player's scores
        with safe and taken discs.

        Args:
            winner_id: id of winner

        Returns:
            True if game has ended
        """
        self.winner_take_vulnerable_discs(winner_id)
        round_scores = [player.round_score for player in self.players]
        print(f"Scoring end of round: {round_scores}")

        scores = [player.end_round() for player in self.players]
        print(f"New score: {scores}")

        self.turn = 0
        self.round += 1

        # player count is 1 based, round is 0 based, for example, in a 3 player game, right after round 2
        #  we have had one round each player and round(3) == player_count(3)
        return self.round == self.player_count

    def set_initial_defence(self):
        """ Roll dice for each player and use them to set initial safe dice. """
        for player_id in range(self.player_count):
            dice = get_unique_dice()
            for d in dice:
                self.play_action(player_id, Action(player_id, d, DiscState.Safe))

    def winners(self) -> Collection[PlayerId]:
        """Return player(s) with highest score"""
        winning_score = max([player.score for player in self.players])
        return [player.player_id for player in self.players if player.score == winning_score]

    def play_round(self, strategies: List[Strategy]):
        """
        Take turns until a round ends.
        """
        end_of_round = False
        while not end_of_round:
            print(self, "\n")
            end_of_round = self.take_turn(self.player_id, strategies[self.player_id])
            self.player_id = (self.player_id + 1) % self.player_count

    def play(self, strategies: List[Strategy]) -> Collection[PlayerId]:
        """Start the game, take turns until round ends"""
        print("Initial board")
        print(self, "\n", "Start Player:", self.start_player, "\n")

        print("Initial defensive rolls")
        self.set_initial_defence()

        game_over = False
        while not game_over:
            self.play_round(strategies)
            game_over = self.end_round(winner_id=self.player_id)

        winners = self.winners()
        print("\nEnd of game\nWinners: ", winners)

        return winners
