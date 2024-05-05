import random
from connection import Connection
from gene import Gene
from config import MUTATE_PROBABILITY


class Individual:
    def __init__(self):
        self.genotype: list[Gene] = list()
        self.fitness = 0
        self.static_fitness = 0
        self.crossing_connections: list[Connection] = list()

    def generate_genotype(self, connections: list[Connection], plate_x: int, plate_y: int) -> None:
        for connection in connections:
            gene = Gene(connection.start_point, connection.end_point)
            gene.generate_gene(connection.start_point, connection.end_point, plate_x, plate_y)
            self.genotype.append(gene)

    def get_intersection_points(self, connections: list[Connection]) -> list[list[Connection]]:
        crossing_connections_by_point = dict()
        intersection_points = list()
        crossing_connections = set()
        for i in range(len(self.genotype)):
            visited_points = self.genotype[i].get_all_visited_points(connections[i].start_point)
            for point in visited_points:
                if point in crossing_connections_by_point.keys():
                    crossing_connections_by_point[point].append(connections[i])
                    for c in crossing_connections_by_point[point]:
                        crossing_connections.add(c)
                else:
                    crossing_connections_by_point[point] = list()
                    crossing_connections_by_point[point].append(connections[i])
        for cross in crossing_connections_by_point.values():
            if len(cross) > 1:
                intersection_points.append(cross)
        self.crossing_connections = crossing_connections
        return intersection_points

    def get_total_outside_paths_number(self, connections: list[Connection], plate_x: int, plate_y: int) -> int:
        total = 0
        for i in range(len(self.genotype)):
            if self.genotype[i].is_path_outside(connections[i].start_point, plate_x, plate_y):
                total += 1
        return total

    def get_total_segments_amount_and_length(self) -> (int, int):
        total = 0
        total_length = 0
        for gene in self.genotype:
            total += gene.get_segments_amount()
            total_length += gene.calculate_total_path_length()
        return total, total_length

    def get_total_outside_path_length(self, connections: list[Connection], plate_x: int, plate_y: int) -> int:
        total = 0
        for i in range(len(self.genotype)):
            total += self.genotype[i].get_outside_path_length(connections[i].start_point, plate_x, plate_y) * connections[i].weight * 5
        return total

    def get_total_outside_path_length_static(self, connections: list[Connection], plate_x: int, plate_y: int) -> int:
        total = 0
        for i in range(len(self.genotype)):
            total += self.genotype[i].get_outside_path_length(connections[i].start_point, plate_x, plate_y) * 5
        return total

    @staticmethod
    def get_intersections_penalty(intersection_points: list[list[Connection]]) -> int:
        total = 0
        point_penalty = 1.0
        for intersection in intersection_points:
            for connection in intersection:
                point_penalty = point_penalty * connection.weight
            total += point_penalty
            point_penalty = 1.0
        return total

    @staticmethod
    def get_intersections_penalty_no_adaptation(intersection_points: list[list[Connection]]) -> int:
        return len(intersection_points)

    def get_total_individual_penalty_no_adaptation(self, connections: list[Connection], weights: dict[str, int], plate_x: int, plate_y: int) -> int:
        intersection_points = self.get_intersection_points(connections)
        total = self.__get_individual_penalty_base(connections, weights, plate_x, plate_y)
        total += self.get_total_outside_path_length_static(connections, plate_x, plate_y) * weights['outside_length']
        total += self.get_intersections_penalty_no_adaptation(intersection_points) * weights['intersections']
        return total

    def calculate_total_individual_penalty(self, connections: list[Connection], weights: dict[str, int], plate_x: int, plate_y: int) -> int:
        intersection_points = self.get_intersection_points(connections)
        total = self.__get_individual_penalty_base(connections, weights, plate_x, plate_y)
        total += self.get_total_outside_path_length(connections, plate_x, plate_y) * weights['outside_length']
        total += self.get_intersections_penalty(intersection_points) * weights['intersections']
        return total

    def mutate_individual(self, plate_x: int, plate_y: int) -> None:
        probability = random.uniform(0, 1)
        if probability >= 1 - MUTATE_PROBABILITY:
            index = random.randrange(len(self.genotype))
            self.genotype[index].mutate_random_segment(plate_x, plate_y)

    def print_genes(self) -> None:
        for gene in self.genotype:
            print(gene, "\n")

    def __get_individual_penalty_base(self, connections: list[Connection], weights: dict[str, int], plate_x: int, plate_y: int) -> int:
        total = 0
        seg_am, _ = self.get_total_segments_amount_and_length()
        total += seg_am * weights['segments_am']
        total += seg_am * weights['path_length']
        total += self.get_total_outside_paths_number(connections, plate_x, plate_y) * weights['outside_number']
        return total
