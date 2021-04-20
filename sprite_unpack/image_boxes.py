from operator import itemgetter
from typing import Tuple, Optional, Generator, Set

from tqdm import tqdm

from sprite_unpack.image import Image
from sprite_unpack.types import Color, Box, Interval, CurrentBox

COLOR_RED = (255, 0, 0, 255)
COLOR_BLUE = (0, 0, 255, 255)
COLOR_YELLOW = (255, 255, 0, 255)


class ImageBoxes:
    def __init__(
        self,
        image: Image,
        min_size: Tuple[int, int] = (10, 10),
        background_color: Optional[Color] = None,
    ) -> None:
        self.image = image
        self._min_width = min_size[0]
        self._min_height = min_size[1]
        self._background_color = background_color
        self._boxes = self._find_boxes()

    def boxes(self) -> Generator[Box, None, None]:
        yield from sorted(self._boxes, key=lambda b: (b[0][1], b[0][0]))

    def _valid_box(self, box: Box) -> bool:
        ((x1, y1), (x2, y2)) = box
        return abs(x1 - x2) > self._min_width and abs(y1 - y2) > self._min_width

    def _overlap(self, interval1: Interval, interval2: Interval) -> bool:
        a1, b1 = interval1
        a2, b2 = interval2
        return not (b1 < a2 or b2 < a1)

    def _join_boxes(self, current_boxes: Set[CurrentBox]) -> Set[CurrentBox]:
        joined_boxes = set()
        current_joined_box = None
        odered_boxes = sorted(current_boxes, key=itemgetter(1))
        for box in odered_boxes:
            if not current_joined_box:
                current_joined_box = box
                continue
            cy, (c1, c2) = current_joined_box
            by, (b1, b2) = box
            if b1 > c2:
                joined_boxes.add(current_joined_box)
                current_joined_box = box
            else:
                current_joined_box = (min(cy, by), (min(c1, b1), max(c2, b2)))

        if current_joined_box:
            joined_boxes.add(current_joined_box)

        return joined_boxes

    def _add_finished_box(self, boxes: Set[Box], finished_box: Box) -> Set[Box]:
        (fx1, fy1), (fx2, fy2) = finished_box
        boxes_to_keep = set()
        for box in boxes:
            (bx1, by1), (bx2, by2) = box
            if fx2 < bx1 or fx1 > bx2 or fy2 < by1 or fy1 > by2:
                boxes_to_keep.add(box)
            else:
                fx1 = min(fx1, bx1)
                fy1 = min(fy1, by1)
                fx2 = max(fx2, bx2)
                fy2 = max(fy2, by2)
        boxes_to_keep.add(((fx1, fy1), (fx2, fy2)))
        return boxes_to_keep

    def _find_current_boxes(
        self, interval: Interval, current_boxes: Set[CurrentBox]
    ) -> Tuple[Set[CurrentBox], Optional[CurrentBox]]:
        boxes = set()
        i1, i2 = interval
        y = -1
        for box in current_boxes:
            (by, box_interval) = box
            b1, b2 = box_interval
            if self._overlap(interval, box_interval):
                if b1 < i1:
                    i1 = b1
                if b2 > i2:
                    i2 = b2
                if y == -1 or by < y:
                    y = by
                boxes.add(box)

        new_box_for_interval = None
        if boxes:
            new_box_for_interval = (y, (i1, i2))

        return (boxes, new_box_for_interval)

    def _find_boxes(self) -> Set[Box]:
        boxes: Set[Box] = set()
        current_boxes: Set[CurrentBox] = set()

        for y in tqdm(range(self.image.height)):
            intervals: Set[Interval] = set()
            interval_start = None
            for x in range(self.image.width):
                color = self.image.color(x, y)
                if interval_start:
                    if color == self._background_color:
                        intervals.add((interval_start, x - 1))
                        interval_start = None
                else:
                    if color != self._background_color:
                        interval_start = x

            new_current_boxes: Set[CurrentBox] = set()
            for interval in intervals:
                old_interval_boxes, new_interval_box = self._find_current_boxes(
                    interval, current_boxes
                )
                if old_interval_boxes and new_interval_box:
                    current_boxes.difference_update(old_interval_boxes)
                    new_current_boxes.add(new_interval_box)
                else:
                    new_current_boxes.add((y, interval))

            new_current_boxes = self._join_boxes(new_current_boxes)

            for (by, (bx1, bx2)) in current_boxes:
                finished_box = ((bx1, by), (bx2, y - 1))
                if self._valid_box(finished_box):
                    boxes = self._add_finished_box(boxes, finished_box)

            # self._debug_boxes(y, boxes, new_current_boxes)

            current_boxes = new_current_boxes
        return boxes

    def _debug_boxes(
        self, y: int, finished_boxes: Set[Box], current_boxes: Set[CurrentBox]
    ):
        filename = "out/{0:04}.png".format(y)
        test_img = self.image.copy()

        for finished_box in finished_boxes:
            test_img.mark(finished_box, COLOR_YELLOW)

        for (cy, (x1, x2)) in current_boxes:
            box: Box = ((x1, cy), (x2, y))
            test_img.mark(box, COLOR_BLUE)

        with open(filename, "wb") as f:
            test_img.write(f)
