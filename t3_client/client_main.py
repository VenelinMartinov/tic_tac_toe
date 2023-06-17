# TODO: This lacks any error handling
import dataclasses
import argparse
import pathlib
from typing import Optional

import requests

CLIENT_CACHE_FILENAME = "t3_cache"


@dataclasses.dataclass
class Game:
    url: str
    game_id: str
    player_token: str

    def print_game_state(self) -> None:
        response = requests.get(self.url + f"/{self.game_id}")
        response.raise_for_status()

        json_response = response.json()
        first_player_name = json_response["first_player_name"]
        second_player_name = (
            json_response["second_player_name"]
            if json_response["second_player_name"] is not None
            else "[EMPTY]"
        )
        print(first_player_name, "vs", second_player_name)

        print("Current turn: " + json_response["current_turn"])
        for line in json_response["game_state"]:
            print(line)

    def play_turn(self, row: int, column: int) -> None:
        response = requests.post(
            self.url + f"/{self.game_id}/play_turn",
            json={"player_token": self.player_token, "row": row, "column": column},
        )
        response.raise_for_status()
        json_response: Optional[dict[str, str]] = response.json()
        if json_response is not None:
            result = json_response.get("result", None)
            if result == "draw":
                self.print_game_state()
                print("Game is drawn")
            else:
                winner = json_response.get("winner")
                self.print_game_state()
                print(f"{winner} won the game")


def handle_game_response(url: str, response: requests.Response) -> Game:
    response.raise_for_status()
    json_response = response.json()
    return Game(
        url=url,
        game_id=json_response["game_id"],
        player_token=json_response["player_token"],
    )


def start_game(url: str, player_name: str) -> Game:
    response = requests.post(url + "/new_game", json={"player_name": player_name})
    return handle_game_response(url=url, response=response)


def join_game(url: str, player_name: str, game_id: str) -> Game:
    response = requests.post(
        url + f"/{game_id}/join", json={"player_name": player_name}
    )
    return handle_game_response(url=url, response=response)


def save_game_info(game: Game, cache_file: pathlib.Path) -> None:
    cache_file.write_text(game.url + "\n" + game.game_id + "\n" + game.player_token)


def load_game_info(cache_file: pathlib.Path) -> Game:
    try:
        game_url, game_id, player_token = cache_file.read_text().splitlines()
    except FileNotFoundError:
        print("No game info saved. Please start or join a game first.")
        exit(1)
    return Game(game_url, game_id, player_token)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tic tac toe client. "
        "The game id, url and player tokens are saved in a local file."
    )
    parser.add_argument("--cache-location", type=str, default=CLIENT_CACHE_FILENAME)
    subparsers = parser.add_subparsers(dest="subparser_name")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument(
        "--url", default="http://localhost:8000", help="server url"
    )
    start_parser.add_argument("--name", required=True)

    join_parser = subparsers.add_parser("join")
    join_parser.add_argument(
        "--url", default="http://localhost:8000", help="server url"
    )
    join_parser.add_argument("--name", required=True, help="player name")
    join_parser.add_argument("--game-id", required=True)

    turn_parser = subparsers.add_parser("turn", help="play a turn")
    turn_parser.add_argument("row", type=int)
    turn_parser.add_argument("column", type=int)

    args = parser.parse_args()

    CACHE_FILE = pathlib.Path(args.cache_location)

    if args.subparser_name == "start":
        game = start_game(args.url, args.name)
        save_game_info(game, CACHE_FILE)
        print("Game ID:", game.game_id)
        return

    if args.subparser_name == "join":
        game = join_game(args.url, args.name, args.game_id)
        save_game_info(game, CACHE_FILE)
        return

    game = load_game_info(CACHE_FILE)

    if args.subparser_name == "state":
        game.print_game_state()

    if args.subparser_name == "turn":
        game.play_turn(args.row, args.column)


if __name__ == "__main__":
    main()
