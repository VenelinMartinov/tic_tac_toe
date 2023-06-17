import fastapi
from PIL import Image
import pytesseract

from server.game_state import Symbol

image_router = fastapi.APIRouter(prefix="/image")

BORDER_CROP = 10 / 100


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
    char= str(pytesseract.image_to_string(image, config="--psm 10", lang="eng"))
    return Symbol.from_char(char)


@image_router.post("/play_turn")
def image_play_turn(file: fastapi.UploadFile) -> None:
    with Image.open(file.file) as uploaded_image:
        image_array: list[list[Symbol]] = []
        for row in range(3):
            column_array: list[Symbol] = []
            for col in range(3):
                cell = crop_cell(uploaded_image, row=row, col=col)
                column_array.append(get_char_from_image(cell))
            image_array.append(column_array)
    print(image_array)
