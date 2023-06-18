from typing import Any
import uuid
import fastapi
import pydantic

from server import game_state, image_processing
from server.dependencies import GamesDict, get_active_games, get_current_game

PLAYER_NAME_MAX_LENGTH = 100
TOKEN_LENGTH = 16

app = fastapi.FastAPI()


class GameBody(pydantic.BaseModel):
    player_name: str = pydantic.Field(max_length=PLAYER_NAME_MAX_LENGTH)


@app.post("/new_game")
def new_game(
    body: GameBody, active_games: GamesDict = fastapi.Depends(get_active_games)
) -> Any:
    new_game_uid = uuid.uuid4()
    active_games[new_game_uid] = game_state.GameState(
        game_id=new_game_uid, first_player_name=body.player_name
    )
    return {
        "game_id": new_game_uid,
        "player_token": active_games[new_game_uid].first_player.token,
    }


@app.get("/{game_id}")
def get_game_state(
    game_id: uuid.UUID, active_games: GamesDict = fastapi.Depends(get_active_games)
) -> Any:
    try:
        current_game = active_games[game_id]
    except KeyError:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND
        )
    second_player = current_game.second_player
    return {
        "game_state": current_game.game_state,
        "first_player_name": current_game.first_player.name,
        "second_player_name": None if second_player is None else second_player.name,
        "current_turn": "first_player"
        if current_game.current_turn_first_player
        else "second_player",
    }


@app.post("/{game_id}/join")
def join_game(
    game_id: uuid.UUID,
    body: GameBody,
    active_games: GamesDict = fastapi.Depends(get_active_games),
) -> Any:
    try:
        current_game = active_games[game_id]
    except KeyError:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND
        )
    if current_game.second_player is not None:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Game is full.",
        )
    new_player = current_game.add_second_player(body.player_name)
    return {
        "game_id": game_id,
        "player_token": new_player.token,
    }


def validate_token(token: str, game: game_state.GameState) -> bool:
    if token == str(game.first_player.token):
        return True
    second_player = game.second_player
    if second_player is not None and token == str(second_player.token):
        return True
    return False


def validate_player_turn(token: str, game: game_state.GameState) -> bool:
    second_player = game.second_player
    if (game.current_turn_first_player and token != str(game.first_player.token)) or (
        second_player is not None
        and not game.current_turn_first_player
        and token != str(second_player.token)
    ):
        return False
    return True


def play_game_turn(
    player_token: str, game: game_state.GameState, move: game_state.Move
) -> Any:
    if not validate_token(player_token, game):
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED
        )

    if not validate_player_turn(player_token, game):
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Not your turn"
        )

    try:
        winner = game.play_turn(move)
    except game_state.InvalidTurn:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Invalid turn"
        )
    if winner is not None:
        return {"result": "won", "winner": winner.name}
    elif game.is_drawn:
        return {"result": "draw"}
    else:
        return None


class PlayTurnBody(pydantic.BaseModel):
    row: int = pydantic.Field(ge=0, le=2)
    column: int = pydantic.Field(ge=0, le=2)


@app.post("/{game_id}/play_turn")
def play_turn(
    request: fastapi.Request,
    body: PlayTurnBody,
    x_player_token: str = fastapi.Header(default=None),
    current_game: game_state.GameState = fastapi.Depends(get_current_game),
) -> Any:
    return play_game_turn(
        x_player_token,
        current_game,
        game_state.Move(col=body.column, row=body.row),
    )


@app.post("/{game_id}/play_turn_image")
def play_turn_image(
    image_file: fastapi.UploadFile,
    x_player_token: str = fastapi.Header(default=None),
    current_game: game_state.GameState = fastapi.Depends(get_current_game),
) -> Any:
    desired_board_state = image_processing.get_board_from_file(image_file.file)
    move = current_game.get_move_difference(desired_board_state)
    if move is None:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Invalid move"
        )
    return play_game_turn(x_player_token, current_game, move)
