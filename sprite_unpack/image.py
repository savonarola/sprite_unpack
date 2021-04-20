from typing import TypeVar, Type, BinaryIO

from PIL import Image as PImage

from sprite_unpack.types import Color, Box

ImageType = TypeVar("ImageType", bound="Image")


class Image:
    image: PImage

    def __init__(self, image: PImage) -> None:
        self.image = image.convert("RGBA")
        self.pix_data = self.image.load()

    @property
    def width(self):
        return self.image.width

    @property
    def height(self):
        return self.image.height

    @classmethod
    def from_io(cls: Type[ImageType], file: BinaryIO) -> ImageType:
        image = PImage.open(file)
        return cls(image)

    def color(self, x: int, y: int) -> Color:
        return self.pix_data[x, y]

    @staticmethod
    def color_to_hex(color: Color) -> str:
        return "#{0:02x}{1:02x}{2:02x}{3:02x}".format(*color)

    def background_color(self) -> Color:
        return self.color(0, 0)

    def copy(self):
        return self.__class__(self.image.copy())

    def make_transparent(self, color: Color):
        for x in range(self.width):
            for y in range(self.height):
                if self.pix_data[x, y] == color:
                    self.pix_data[x, y] = (0, 0, 0, 0)

    def subimage(self, box: Box) -> "Image":
        ((x1, y1), (x2, y2)) = box
        if x1 > x2:
            (x1, x2) = (x2, x1)
        if y1 > y2:
            (y1, y2) = (y2, y1)

        return self.__class__(self.image.crop((x1, y1, x2 + 1, y2 + 1)))

    def mark(self, box: Box, color: Color):
        ((x1, y1), (x2, y2)) = box
        if x1 > x2:
            (x1, x2) = (x2, x1)
        if y1 > y2:
            (y1, y2) = (y2, y1)

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                self.pix_data[x, y] = color

    def write(self, file: BinaryIO) -> None:
        self.image.save(file, format="PNG")
