import argparse
from pathlib import Path

from sprite_unpack.sprite_sheet import SpriteSheet


def dir_path(path):
    if Path(path).is_dir():
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--sheet-image",
        type=argparse.FileType("rb"),
        required=True,
        help="Sheet image to cut (in PNG format)",
    )
    parser.add_argument(
        "-o", "--outdir", type=dir_path, required=True, help="Output directory"
    )
    parser.add_argument(
        "-b",
        "--background",
        type=str,
        help="4-byte RGBA background color in hex format (00FFAAFF)",
    )
    parser.add_argument(
        "--min-width",
        default=10,
        help="Minimal width for a sprite image in the sprite sheet for not to be ignored",
    )
    parser.add_argument(
        "--min-height",
        default=10,
        help="Minimal height for a sprite image in the sprite sheet for not to be ignored",
    )
    args = parser.parse_args()

    background = None
    if args.background:
        background = int(args.background, base=16)
    min_size = (args.min_width, args.min_height)
    sheet = SpriteSheet(args.sheet_image, min_size, background=background)
    print(f"Found {len(sheet.boxes)} images")
    sheet.write(Path(args.outdir))


if __name__ == "__main__":
    main()
