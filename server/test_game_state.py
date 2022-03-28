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
        [game_state.Symbols.X, game_state.Symbols.O, game_state.Symbols.O],
        [game_state.Symbols.X, game_state.Symbols.O, game_state.Symbols.EMPTY],
        [game_state.Symbols.EMPTY, game_state.Symbols.EMPTY, game_state.Symbols.EMPTY],
    ]

    winner = game.play_turn(2, 0)
    assert winner == game.first_player


def test_random_play_doesnt_win(game: game_state.GameState) -> None:
    game.game_state = [
        [game_state.Symbols.EMPTY, game_state.Symbols.EMPTY, game_state.Symbols.EMPTY],
        [game_state.Symbols.EMPTY, game_state.Symbols.EMPTY, game_state.Symbols.EMPTY],
        [game_state.Symbols.EMPTY, game_state.Symbols.EMPTY, game_state.Symbols.EMPTY],
    ]
    winner = game.play_turn(1, 1)
    assert winner is None
