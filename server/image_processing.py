from typing import BinaryIO
from PIL import Image
import pytesseract

from server.game_state import Symbol


BORDER_CROP = 10 / 100
IMAGE_THRESHOLD = 100


def preprocess_image(image: Image.Image) -> Image.Image:
    grayscaled_image = image.convert("L")
    binarized_image = grayscaled_image.point(
        lambda p: 255 if p > IMAGE_THRESHOLD else 0
    )
    return binarized_image


def crop_cell(image: Image.Image, *, row: int, col: int) -> Image.Image:
    cropped_height = image.height // 3
    cropped_width = image.width // 3
    return image.crop(
        (
            int((col + BORDER_CROP) * cropped_width),
            int((row + BORDER_CROP) * cropped_height),
            int(((col + 1) - BORDER_CROP) * cropped_width),
            int(((row + 1) - BORDER_CROP) * cropped_height),
        )
    )


def get_char_from_image(image: Image.Image) -> Symbol:
    char = str(pytesseract.image_to_string(image, config="--psm 10", lang="eng"))
    return Symbol.from_char(char[0] if len(char) > 0 else " ")


def get_board_from_file(file: BinaryIO) -> list[list[Symbol]]:
    with Image.open(file) as uploaded_image:
        preprocessed_image = preprocess_image(uploaded_image)
        image_array: list[list[Symbol]] = []
        for row in range(3):
            column_array: list[Symbol] = []
            for col in range(3):
                cell = crop_cell(preprocessed_image, row=row, col=col)
                column_array.append(get_char_from_image(cell))
            image_array.append(column_array)
    return image_array
