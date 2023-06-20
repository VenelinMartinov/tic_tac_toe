from __future__ import annotations
from typing import Optional
import dataclasses
import enum
import random
import uuid


class InvalidTurn(Exception):
    pass


class Symbol(enum.Enum):
    X = "X"
    O = "O"
    EMPTY = "_"

    @staticmethod
    def from_char(char: str) -> Symbol:
        stripped = char.strip()
        if stripped in ["o", "O"]:
            return Symbol.O
        if stripped in ["x", "X", "4"]:
            return Symbol.X
        return Symbol.EMPTY


@dataclasses.dataclass
class Move:
    row: int
    col: int


@dataclasses.dataclass
class Player:
    name: str
    token: uuid.UUID

    def __init__(self, name: str) -> None:
        self.name = name
        self.token = uuid.uuid4()


class InvalidGameStateRequested(Exception):
    pass


@dataclasses.dataclass
class GameState:
    game_id: uuid.UUID
    game_state: list[list[Symbol]]
    first_player: Player
    current_turn_first_player: bool
    first_player_starts: bool
    turns_played: int = 0
    winner: Optional[Player] = None
    second_player: Optional[Player] = None

    def __init__(self, game_id: uuid.UUID, first_player_name: str) -> None:
        self.game_id = game_id
        self.game_state = [[Symbol.EMPTY] * 3 for _ in range(3)]
        self.first_player = Player(name=first_player_name)
        self.first_player_starts = random.choice([True, False])
        self.current_turn_first_player = self.first_player_starts

    def add_second_player(self, player_name: str) -> Player:
        self.second_player = Player(player_name)
        return self.second_player

    def _is_winning_move(self, move: Move) -> bool:
        current_play = self.game_state[move.row][move.col]
        assert current_play != Symbol.EMPTY
        column_win = all(self.game_state[move.row][i] == current_play for i in range(3))
        row_win = all(self.game_state[i][move.col] == current_play for i in range(3))
        left_diag_win = (move.col == move.row) and all(
            self.game_state[i][i] == current_play for i in range(3)
        )
        right_diag_win = (move.col + move.row == 2) and all(
            self.game_state[i][2 - i] == current_play for i in range(3)
        )
        return column_win or row_win or left_diag_win or right_diag_win

    def play_turn(self, move: Move) -> Optional[Player]:
        if self.game_state[move.row][move.col] != Symbol.EMPTY:
            raise InvalidTurn

        current_play = (
            Symbol.X
            if (
                (self.first_player_starts and self.current_turn_first_player)
                or (not self.first_player_starts and not self.current_turn_first_player)
            )
            else Symbol.O
        )
        self.game_state[move.row][move.col] = current_play
        self.turns_played += 1

        if self._is_winning_move(move):
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

    def get_move_difference(self, board: list[list[Symbol]]) -> Move | None:
        move = None
        for row in range(3):
            for col in range(3):
                if board[row][col] != self.game_state[row][col]:
                    if move is not None:
                        raise InvalidGameStateRequested(
                            f"more than one move difference {board} {self.game_state}"
                        )
                    move = Move(row=row, col=col)
        return move
