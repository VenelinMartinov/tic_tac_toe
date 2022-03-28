from typing import Optional
import dataclasses
import enum
import random
import uuid


class InvalidTurn(Exception):
    pass


class Symbols(enum.Enum):
    X = "X"
    O = "O"
    EMPTY = "_"


@dataclasses.dataclass
class Player:
    name: str
    token: uuid.UUID

    def __init__(self, name: str) -> None:
        self.name = name
        self.token = uuid.uuid4()


@dataclasses.dataclass
class GameState:
    game_id: uuid.UUID
    game_state: list[list[Symbols]]
    first_player: Player
    current_turn_first_player: bool
    first_player_starts: bool
    turns_played: int = 0
    winner: Optional[Player] = None
    second_player: Optional[Player] = None

    def __init__(self, game_id: uuid.UUID, first_player_name: str) -> None:
        self.game_id = game_id
        self.game_state = [[Symbols.EMPTY] * 3 for _ in range(3)]
        self.first_player = Player(name=first_player_name)
        self.first_player_starts = random.choice([True, False])
        self.current_turn_first_player = self.first_player_starts

    def add_second_player(self, player_name: str) -> Player:
        self.second_player = Player(player_name)
        return self.second_player

    def _is_winning_move(self, row: int, column: int) -> bool:
        current_play = self.game_state[row][column]
        assert current_play != Symbols.EMPTY
        column_win = all(self.game_state[row][i] == current_play for i in range(3))
        row_win = all(self.game_state[i][column] == current_play for i in range(3))
        left_diag_win = (column == row) and all(
            self.game_state[i][i] == current_play for i in range(3)
        )
        right_diag_win = (column + row == 2) and all(
            self.game_state[i][2 - i] == current_play for i in range(3)
        )
        return column_win or row_win or left_diag_win or right_diag_win

    def play_turn(self, column: int, row: int) -> Optional[Player]:
        if self.game_state[row][column] != Symbols.EMPTY:
            raise InvalidTurn

        current_play = (
            Symbols.X
            if (
                (self.first_player_starts and self.current_turn_first_player)
                or (not self.first_player_starts and not self.current_turn_first_player)
            )
            else Symbols.O
        )
        self.game_state[row][column] = current_play
        self.turns_played += 1

        if self._is_winning_move(row, column):
            self.winner = (
                self.first_player
                if self.current_turn_first_player
                else self.second_player
            )

        self.current_turn_first_player = not self.current_turn_first_player
        return self.winner

    @property
    def is_drawn(self) -> bool:
        return self.turns_played == 9 and self.winner is None
