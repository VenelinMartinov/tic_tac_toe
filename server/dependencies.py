import uuid

import fastapi

from server import game_state


GamesDict = dict[uuid.UUID, game_state.GameState]

ALL_GAMES: GamesDict = {}


def get_active_games() -> GamesDict:
    return ALL_GAMES


def get_current_game(
    game_id: uuid.UUID,
    active_games: GamesDict = fastapi.Depends(get_active_games),
) -> game_state.GameState:
    try:
        return active_games[game_id]
    except KeyError:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND
        )
