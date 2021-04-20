from pathlib import Path
from typing import BinaryIO, Optional, Tuple

from sprite_unpack.image import Image
from sprite_unpack.image_boxes import ImageBoxes
from sprite_unpack.types import Color


class FileIds:
    def __init__(self, filename):
        self.basename = Path(filename).stem

    def ids(self):
        n = 0
        while True:
            yield f"{self.basename}_{n:03}"
            n += 1


class SpriteSheet:
    def __init__(
        self,
        file: BinaryIO,
        min_size: Tuple[int, int],
        background: Optional[Color] = None,
    ) -> None:
        self.filename = Path(file.name)
        self.image = Image.from_io(file)
        if background:
            self.background_color = background
        else:
            self.background_color = self.image.background_color()

        self.image_boxes = ImageBoxes(
            self.image, background_color=self.background_color, min_size=min_size
        )
        self.file_ids = FileIds(self.filename)

    @property
    def boxes(self):
        return list(self.image_boxes.boxes())

    def write(self, outdir: Path) -> None:
        outdir.mkdir(parents=True, exist_ok=True)

        for (box, file_id) in zip(self.boxes, self.file_ids.ids()):
            subimage = self.image.subimage(box)
            subimage.make_transparent(self.background_color)

            filename = outdir.joinpath(f"{file_id}.png")
            with open(filename, "wb") as file:
                subimage.write(file)
