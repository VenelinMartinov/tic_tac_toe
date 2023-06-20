from server.image_processing import get_board_from_file
from server.game_state import Symbol


def test_image() -> None:
    with open("tic-tac-toe-example.png", "rb") as image_file:
        board = get_board_from_file(image_file)
    assert board == [
        [Symbol.X, Symbol.O, Symbol.EMPTY],
        [Symbol.X, Symbol.O, Symbol.EMPTY],
        [Symbol.X, Symbol.EMPTY, Symbol.EMPTY],
    ]


def test_hand_drawn() -> None:
    with open("hand_drawn.jpg", "rb") as image_file:
        board = get_board_from_file(image_file)
    assert board == [
        [Symbol.X, Symbol.O, Symbol.EMPTY],
        [Symbol.X, Symbol.O, Symbol.EMPTY],
        [Symbol.X, Symbol.EMPTY, Symbol.EMPTY],
    ]