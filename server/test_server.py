import uuid
import pytest
from fastapi import testclient

from server import dependencies, server_main, game_state


@pytest.fixture
def test_client() -> testclient.TestClient:
    return testclient.TestClient(server_main.app)


@pytest.fixture
def game() -> game_state.GameState:
    game_id = uuid.uuid4()
    games = {game_id: game_state.GameState(game_id, first_player_name="player1")}
    games[game_id].first_player_starts = True
    games[game_id].current_turn_first_player = True

    def return_games() -> dependencies.GamesDict:
        return games

    server_main.app.dependency_overrides[dependencies.get_active_games] = return_games
    return games[game_id]


def test_create_game(test_client: testclient.TestClient) -> None:
    response = test_client.post("/new_game", json={"player_name": "player1"})
    assert response.status_code == 200


def test_join_game(
    test_client: testclient.TestClient, game: game_state.GameState
) -> None:
    response = test_client.post(
        f"/{game.game_id}/join", json={"player_name": "player2"}
    )
    assert response.status_code == 200


def test_get_state(
    test_client: testclient.TestClient, game: game_state.GameState
) -> None:
    response = test_client.get(f"/{game.game_id}")
    assert response.status_code == 200


def test_play_turn(
    test_client: testclient.TestClient, game: game_state.GameState
) -> None:
    response = test_client.post(
        f"/{game.game_id}/play_turn",
        json={"player_token": str(game.first_player.token), "row": 0, "column": 0},
    )
    assert response.status_code == 200
