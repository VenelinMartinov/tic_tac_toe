import uuid
import pytest

from server import game_state


@pytest.fixture
def game() -> game_state.GameState:
    return game_state.GameState(game_id=uuid.uuid4(), first_player_name="player1")


def test_draw(game: game_state.GameState) -> None:
    game.turns_played = 9
    assert game.is_drawn


def test_play_winning_turn(game: game_state.GameState) -> None:
    game.game_state = [["X", "O", "O"], ["X", "O", "_"], ["_", "_", "_"]]
    game.first_player_starts = True
    game.current_turn_first_player = True
    winner = game.play_turn(2, 0)
    assert winner == game.first_player
