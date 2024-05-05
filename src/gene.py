import random
from connection import Point, Direction, Segment


class Gene:
    def __init__(self, start_point: Point, end_point: Point):
        self.segments: list[Segment] = list()
        self.start_point = start_point
        self.end_point = end_point

    def generate_gene(self, start_point: Point, end_point: Point, plate_x: int, plate_y: int) -> None:
        current_p = Point(start_point.x, start_point.y)
        last_direction = -1
        while not current_p.__eq__(end_point):
            new_data = self.generate_next_segment(current_p, end_point, last_direction, plate_x, plate_y)
            last_direction = new_data[1]
            current_p.update_point_coordinates(new_data[0])

    def generate_next_segment(
            self,
            current_point: Point,
            end_point: Point,
            last_dir: Direction,
            plate_x: int,
            plate_y: int
    ) -> (Segment, Direction):
        next_segment = Segment()

        if current_point.x == end_point.x:
            if last_dir != Direction.VERTICAL:
                current_dir = Direction.VERTICAL
                segment_len = random.randint(1, abs(current_point.y - end_point.y))
                next_segment.path_length = segment_len
                if current_point.y > end_point.y:
                    next_segment.direction = Direction.DOWN
                else:
                    next_segment.direction = Direction.UP
            else:
                current_dir = Direction.HORIZONTAL
                segment_len = random.randint(1, abs(plate_x - current_point.x))
                random_dir = Direction.get_random_direction(Direction.LEFT, Direction.RIGHT)
                next_segment.path_length = segment_len
                next_segment.direction = random_dir

        elif current_point.y == end_point.y:
            if last_dir != Direction.HORIZONTAL:
                current_dir = Direction.HORIZONTAL
                segment_len = random.randint(1, abs(current_point.x - end_point.x))
                next_segment.path_length = segment_len
                if current_point.x > end_point.x:
                    next_segment.direction = Direction.LEFT
                else:
                    next_segment.direction = Direction.RIGHT
            else:
                current_dir = Direction.VERTICAL
                segment_len = random.randint(1, abs(plate_y - current_point.y))
                random_dir = Direction.get_random_direction(Direction.UP, Direction.DOWN)
                next_segment.path_length = segment_len
                next_segment.direction = random_dir

        else:
            directions = current_point.get_available_directions(end_point, last_dir)
            random_dir = directions[random.randint(0, len(directions) - 1)]
            if last_dir == Direction.HORIZONTAL:
                segment_len = random.randint(1, abs(current_point.y - end_point.y))
                current_dir = Direction.VERTICAL
            elif last_dir == Direction.VERTICAL:
                segment_len = random.randint(1, abs(current_point.x - end_point.x))
                current_dir = Direction.HORIZONTAL
            else:
                if random_dir == Direction.RIGHT or random_dir == Direction.LEFT:
                    segment_len = random.randint(1, abs(current_point.x - end_point.x))
                    current_dir = Direction.HORIZONTAL
                else:
                    segment_len = random.randint(1, abs(current_point.y - end_point.y))
                    current_dir = Direction.VERTICAL

            next_segment.path_length = segment_len
            next_segment.direction = random_dir

        self.segments.append(next_segment)

        return next_segment, current_dir

    def mutate_random_segment(self, plate_x: int, plate_y: int) -> None:
        if len(self.segments) <= 1:
            index = 0
        else:
            index = random.randrange(0, len(self.segments))

        segment_to_mutate: Segment = self.segments[index]
        if segment_to_mutate.direction == Direction.UP or segment_to_mutate.direction == Direction.DOWN:
            shift_direction = random.choice([Direction.LEFT, Direction.RIGHT])
            plate_edge = plate_x
        else:
            shift_direction = random.choice([Direction.UP, Direction.DOWN])
            plate_edge = plate_y

        shift_length = random.randint(1, plate_edge - 1)
        mutated_segments = []
        if segment_to_mutate.path_length > 1 and bool(random.getrandbits(1)):
            split_ind = random.randint(1, segment_to_mutate.path_length - 1)
            if bool(random.getrandbits(1)):
                mutated_segments.append(Segment(shift_length, shift_direction))
                mutated_segments.append(Segment(split_ind, segment_to_mutate.direction))
                mutated_segments.append(Segment(shift_length, Gene.get_opposite_direction(shift_direction)))
                mutated_segments.append(Segment(segment_to_mutate.path_length - split_ind, segment_to_mutate.direction))
            else:
                mutated_segments.append(Segment(split_ind, segment_to_mutate.direction))
                mutated_segments.append(Segment(shift_length, shift_direction))
                mutated_segments.append(Segment(segment_to_mutate.path_length - split_ind, segment_to_mutate.direction))
                mutated_segments.append(Segment(shift_length, Gene.get_opposite_direction(shift_direction)))
        else:
            mutated_segments.append(Segment(shift_length, shift_direction))
            mutated_segments.append(Segment(segment_to_mutate.path_length, segment_to_mutate.direction))
            mutated_segments.append(Segment(shift_length, Gene.get_opposite_direction(shift_direction)))
        del self.segments[index]
        self.segments[index:index] = mutated_segments
        self.normalize_steps()

    def normalize_steps(self) -> None:
        new_segments = []
        if len(self.segments) < 2:
            return
        for segment in self.segments:
            if len(new_segments) == 0:
                new_segments.append(segment)
                continue
            last_segment = new_segments[-1]
            last_index = len(new_segments) - 1
            if last_segment.direction == segment.direction:
                new_segments[last_index].path_length += segment.path_length
                continue
            if last_segment.direction == Gene.get_opposite_direction(segment.direction):
                diff = last_segment.path_length - segment.path_length
                if diff == 0:
                    new_segments.remove(last_segment)
                    continue
                if diff < 0:
                    last_segment.direction = Gene.get_opposite_direction(last_segment.direction)
                last_segment.path_length = abs(diff)
                continue
            new_segments.append(segment)
        self.segments = new_segments

    @staticmethod
    def get_opposite_direction(direction: Direction) -> Direction:
        if direction == Direction.UP:
            return Direction.DOWN
        elif direction == Direction.DOWN:
            return Direction.UP
        elif direction == Direction.LEFT:
            return Direction.RIGHT
        else:
            return Direction.LEFT

    def get_all_visited_points(self, start_point: Point) -> list[Point]:
        visited = list()
        visited.append(start_point)
        next_point = start_point
        for segment in self.segments:
            for i in range(segment.path_length):
                next_point = next_point.get_next_point(segment.direction, 1)
                visited.append(next_point)
        return visited

    def calculate_total_path_length(self) -> int:
        length = 0
        for segment in self.segments:
            length += segment.path_length
        return length

    def get_segments_amount(self):
        return len(self.segments)

    def is_path_outside(self, start_point: Point, plate_x: int, plate_y: int) -> bool:
        current_p = Point(start_point.x, start_point.y)
        for segment in self.segments:
            if segment.direction == Direction.UP:
                current_p.y += segment.path_length
                if current_p.y > plate_y:
                    return True
            if segment.direction == Direction.DOWN:
                current_p.y -= segment.path_length
                if current_p.y < 0:
                    return True
            if segment.direction == Direction.LEFT:
                current_p.x -= segment.path_length
                if current_p.x < 0:
                    return True
            if segment.direction == Direction.RIGHT:
                current_p.x += segment.path_length
                if current_p.x > plate_x:
                    return True
        return False

    def get_outside_path_length(self, start_point: Point, plate_x: int, plate_y: int) -> int:
        current_p = Point(start_point.x, start_point.y)
        outside_length = 0

        for segment in self.segments:
            outside_length += Gene.calculate_outside_length(current_p.x, current_p.y,
                                                            segment.path_length, segment.direction, plate_x, plate_y)
            if segment.direction == Direction.UP:
                current_p.y += segment.path_length
            if segment.direction == Direction.DOWN:
                current_p.y -= segment.path_length
            if segment.direction == Direction.LEFT:
                current_p.x -= segment.path_length
            if segment.direction == Direction.RIGHT:
                current_p.x += segment.path_length

        return outside_length

    @staticmethod
    def calculate_outside_length(point_x: int, point_y: int, step: int, direction: Direction, plate_x: int, plate_y: int) -> int:
        length = 0
        for i in range(step):
            next_x = point_x
            next_y = point_y
            if direction == Direction.UP:
                next_y += 1
            if direction == Direction.DOWN:
                next_y -= 1
            if direction == Direction.LEFT:
                next_x -= 1
            if direction == Direction.RIGHT:
                next_x += 1
            if not (Point.is_point_inside_coordinates(point_x, point_y, plate_x, plate_y) and Point.is_point_inside_coordinates(next_x, next_y, plate_x, plate_y)):
                length += 1
            point_x = next_x
            point_y = next_y
        return length

    def __str__(self) -> str:
        ret = ""
        for segment in self.segments:
            ret += segment.__str__()
            ret += "\n"
        return ret
