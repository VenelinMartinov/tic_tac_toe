import uuid

from server import game_state


GamesDict = dict[uuid.UUID, game_state.GameState]

ALL_GAMES: GamesDict = {}


def get_active_games() -> GamesDict:
    return ALL_GAMES
