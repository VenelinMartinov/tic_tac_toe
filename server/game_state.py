from typing import Optional
import dataclasses
import random
import uuid


class InvalidTurn(Exception):
    pass


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
    game_state: list[list[str]]
    first_player: Player
    current_turn_first_player: bool
    first_player_starts: bool
    turns_played: int = 0
    winner: Optional[Player] = None
    second_player: Optional[Player] = None

    def __init__(self, game_id: uuid.UUID, first_player_name: str) -> None:
        self.game_id = game_id
        self.game_state = [["_"] * 3 for _ in range(3)]
        self.first_player = Player(name=first_player_name)
        self.first_player_starts = random.choice([True, False])
        self.current_turn_first_player = self.first_player_starts

    def add_second_player(self, player_name: str) -> Player:
        self.second_player = Player(player_name)
        return self.second_player

    def _is_winning_move(self, column: int, row: int) -> bool:
        current_play = self.game_state[column][row]
        assert current_play != "_"
        return (
            all(self.game_state[column][i] == current_play for i in range(3))
            or all(self.game_state[i][row] for i in range(3))
            or (column == row and all(self.game_state[i][i] for i in range(3)))
            or (column + row == 2 and all(self.game_state[i][2 - i] for i in range(3)))
        )

    def play_turn(self, column: int, row: int) -> Optional[Player]:
        if self.game_state[column][row] != "_":
            print(self.game_state)
            raise InvalidTurn

        current_play = (
            "X"
            if (self.first_player_starts and self.current_turn_first_player)
            else "O"
        )
        self.game_state[column][row] = current_play
        self.turns_played += 1

        if self._is_winning_move(column, row):
            self.winner = (
                self.first_player
                if self.current_turn_first_player
                else self.second_player
            )
            return self.winner
        return None

    @property
    def is_drawn(self) -> bool:
        return self.turns_played == 9 and self.winner is None
