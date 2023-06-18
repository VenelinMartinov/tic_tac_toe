import uuid
import pytest

from server import game_state


@pytest.fixture
def game() -> game_state.GameState:
    game = game_state.GameState(game_id=uuid.uuid4(), first_player_name="player1")
    game.first_player_starts = True
    game.current_turn_first_player = True
    return game


def test_draw(game: game_state.GameState) -> None:
    game.turns_played = 9
    assert game.is_drawn


def test_play_winning_turn(game: game_state.GameState) -> None:
    game.game_state = [
        [game_state.Symbol.X, game_state.Symbol.O, game_state.Symbol.O],
        [game_state.Symbol.X, game_state.Symbol.O, game_state.Symbol.EMPTY],
        [game_state.Symbol.EMPTY, game_state.Symbol.EMPTY, game_state.Symbol.EMPTY],
    ]

    winner = game.play_turn(game_state.Move(row=2, col=0))
    assert winner == game.first_player


def test_random_play_doesnt_win(game: game_state.GameState) -> None:
    game.game_state = [
        [game_state.Symbol.EMPTY, game_state.Symbol.EMPTY, game_state.Symbol.EMPTY],
        [game_state.Symbol.EMPTY, game_state.Symbol.EMPTY, game_state.Symbol.EMPTY],
        [game_state.Symbol.EMPTY, game_state.Symbol.EMPTY, game_state.Symbol.EMPTY],
    ]
    winner = game.play_turn(game_state.Move(row=1, col=1))
    assert winner is None
