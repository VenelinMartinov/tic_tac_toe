from typing import Any
import uuid
import fastapi
import pydantic

from server import game_state

PLAYER_NAME_MAX_LENGTH = 100
TOKEN_LENGTH = 16

app = fastapi.FastAPI()

GamesDict = dict[uuid.UUID, game_state.GameState]

ALL_GAMES: GamesDict = {}


def get_active_games() -> GamesDict:
    return ALL_GAMES


class NewGameBody(pydantic.BaseModel):
    player_name: str = pydantic.Field(max_length=PLAYER_NAME_MAX_LENGTH)


@app.post("/new_game")
async def new_game(
    body: NewGameBody, active_games: GamesDict = fastapi.Depends(get_active_games)
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
async def get_game_state(
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


class JoinGameBody(pydantic.BaseModel):
    player_name: str = pydantic.Field(max_length=PLAYER_NAME_MAX_LENGTH)


@app.post("/{game_id}/join")
async def join_game(
    game_id: uuid.UUID,
    body: JoinGameBody,
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


def validate_token(token: uuid.UUID, game: game_state.GameState) -> bool:
    player_tokens = [game.first_player.token]
    second_player = game.second_player
    if second_player is not None:
        player_tokens.append(second_player.token)

    if token not in player_tokens:
        return False
    return True


def validate_player_turn(token: uuid.UUID, game: game_state.GameState) -> None:
    second_player = game.second_player
    if (game.current_turn_first_player and token != game.first_player.token) or (
        second_player is not None
        and not game.current_turn_first_player
        and token != second_player.token
    ):
        return False
    return True


class PlayTurnBody(pydantic.BaseModel):
    player_token: uuid.UUID
    row: int = pydantic.Field(ge=0, le=2)
    column: int = pydantic.Field(ge=0, le=2)


@app.post("/{game_id}/play_turn")
async def play_turn(
    game_id: uuid.UUID,
    body: PlayTurnBody,
    active_games: GamesDict = fastapi.Depends(get_active_games),
) -> Any:
    try:
        current_game = active_games[game_id]
    except KeyError:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND
        )

    if not validate_token(body.player_token, current_game):
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED
        )

    if not validate_player_turn(body.player_token, current_game):
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Not your turn"
        )

    try:
        winner = current_game.play_turn(body.column, body.row)
    except game_state.InvalidTurn:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Invalid turn"
        )
    if winner is not None:
        return {"result": "won", "winner": winner.name}
    elif current_game.is_drawn:
        return {"result": "draw"}
    else:
        return None
