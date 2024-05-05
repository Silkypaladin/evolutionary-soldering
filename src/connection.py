from enum import Enum
import random


class Direction(Enum):
    SAME_LEVEL = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    HORIZONTAL = 5
    VERTICAL = 6

    @staticmethod
    def get_random_direction(dir_one: "Direction", dir_two: "Direction") -> "Direction":
        rand = random.randint(1, 2)
        if rand == 1:
            return dir_one
        return dir_two


class Segment:
    def __init__(self, segment_length=0, direction=0):
        self.path_length = segment_length
        self.direction = direction

    def __str__(self) -> str:
        return f"Length: {self.path_length}, Direction: {self.direction}"


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def get_available_directions(self, other: "Point", last_dir: Direction) -> list[Direction]:
        directions = list()
        if last_dir != Direction.HORIZONTAL:
            if self.x < other.x:
                directions.append(Direction.RIGHT)
            elif self.x > other.x:
                directions.append(Direction.LEFT)
        if last_dir != Direction.VERTICAL:
            if self.y < other.y:
                directions.append(Direction.UP)
            elif self.y > other.y:
                directions.append(Direction.DOWN)
        return directions

    def update_point_coordinates(self, segment: Segment) -> None:
        if segment.direction == Direction.UP:
            self.y += segment.path_length
        elif segment.direction == Direction.DOWN:
            self.y -= segment.path_length
        elif segment.direction == Direction.LEFT:
            self.x -= segment.path_length
        elif segment.direction == Direction.RIGHT:
            self.x += segment.path_length

    def get_next_point(self, direction: Direction, step: int) -> "Point":
        next_point = Point(self.x, self.y)
        if direction == Direction.UP:
            next_point.y += step
        elif direction == Direction.DOWN:
            next_point.y -= step
        elif direction == Direction.LEFT:
            next_point.x -= step
        elif direction == Direction.RIGHT:
            next_point.x += step
        return next_point

    @staticmethod
    def is_point_inside_coordinates(x: int, y: int, plate_x, plate_y) -> bool:
        if 0 < x < plate_x:
            if 0 < y < plate_y:
                return True
        return False

    def __str__(self) -> str:
        return f"Point ({self.x}, {self.y})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class Connection:
    def __init__(self, start_point: Point, end_point: Point):
        self.start_point = start_point
        self.end_point = end_point
        self.weight = 1

    def get_right_directions(self) -> (Direction, Direction):
        if self.start_point.x < self.end_point.x:
            dir_x = Direction.RIGHT
        elif self.start_point.x == self.end_point.x:
            dir_x = Direction.SAME_LEVEL
        else:
            dir_x = Direction.LEFT

        if self.start_point.y < self.end_point.y:
            dir_y = Direction.UP
        elif self.start_point.y == self.end_point.y:
            dir_y = Direction.SAME_LEVEL
        else:
            dir_y = Direction.DOWN

        return dir_x, dir_y

    def __str__(self) -> str:
        return f"{self.start_point} -> {self.end_point}"
