import uuid
import httpx
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
        json={"row": 0, "column": 0},
        headers={"x-player-token": str(game.first_player.token)},
    )
    assert response.status_code == 200


def test_whole_game(test_client: testclient.TestClient) -> None:
    response = test_client.post("/new_game", json={"player_name": "player1"})
    assert response.status_code == 200
    game_id = response.json()["game_id"]
    player_one_token = response.json()["player_token"]

    response = test_client.post(f"/{game_id}/join", json={"player_name": "player2"})
    assert response.status_code == 200
    player_two_token = response.json()["player_token"]

    response = test_client.get(f"/{game_id}")
    assert response.status_code == 200
    first_player_first = response.json()["current_turn"] == "first_player"

    first_player_token = player_one_token if first_player_first else player_two_token
    second_player_token = player_two_token if first_player_first else player_one_token

    def play_turn(token: str, *, row: int, col: int) -> httpx.Response:
        response = test_client.post(
            f"/{game_id}/play_turn",
            json={"row": row, "column": col},
            headers={"x-player-token": token},
        )
        assert response.status_code == 200
        return response

    play_turn(first_player_token, row=0, col=0)
    play_turn(second_player_token, row=0, col=1)
    play_turn(first_player_token, row=1, col=0)
    play_turn(second_player_token, row=1, col=1)

    with open("tic-tac-toe-example.png", "rb") as image_file:
        response = response = test_client.post(
            f"/{game_id}/play_turn_image",
            headers={"x-player-token": first_player_token},
            files={"image_file": image_file},
        )
    assert response.json()["winner"] == ("player1" if first_player_first else "player2")
