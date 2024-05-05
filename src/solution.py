from connection import Connection, Point
from population import Population
from config import PENALTY_WEIGHTS
from plotter import *


class Solution:
    def __init__(self):
        self.population = Population()
        self.start_points: list[Point] = list()

    def read_solution_from_file(self, filename: str) -> None:
        with open(filename) as fp:
            for count, line in enumerate(fp):
                data = line.rstrip('\n').split(';')
                if count == 0:
                    self.population.plate_x = int(data[0])
                    self.population.plate_y = int(data[1])
                else:
                    self.population.connections.append(Connection(Point(int(data[0]), int(data[1])),
                                                                  Point(int(data[2]), int(data[3]))))
                    self.start_points.append(Point(int(data[0]), int(data[1])))

    def test_genetic_algorithm(self, iterations: int, population_size: int) -> None:
        self.population.set_weights(PENALTY_WEIGHTS)
        for i in range(10):
            self.population.run_genetic_algorithm(iterations, population_size)
            for conn in self.population.connections:
                conn.weight = 1
            self.population.sort_population_by_fitness(self.population.population)
            for j in range(3):
                draw_path(self.population.population[j].genotype, self.population.plate_x, self.population.plate_y,
                          self.start_points)
            self.population.population.clear()

    def test_operators(self):
        self.population.set_weights(PENALTY_WEIGHTS)
        self.population.generate_population(5)
        self.population.sort_population_by_fitness(self.population.population)
        for i in range(len(self.population.population)):
            print("Individual ", i, ": ",
                  self.population.population[i].calculate_total_individual_penalty(self.population.connections,
                                                                                   self.population.weights,
                                                                                   self.population.plate_x,
                                                                                   self.population.plate_y))
        res = self.population.roulette_selection()
        print("Roulette: ",
              res[0].calculate_total_individual_penalty(self.population.connections, self.population.weights,
                                                        self.population.plate_x, self.population.plate_y))
        res = self.population.tournament_selection(5)
        print("Tournament: ",
              res[0].calculate_total_individual_penalty(self.population.connections, self.population.weights,
                                                        self.population.plate_x, self.population.plate_y))
        print("Before crossing: ", self.population.population[0].__hash__(), " ",
              self.population.population[1].__hash__())
        res = self.population.cross_two_individuals(self.population.population[0], self.population.population[1])
        print("Result of crossing: ", res[0].__hash__(), res[1].__hash__())

    def __str__(self) -> str:
        conns = ""
        for c in self.population.connections:
            conns += c.__str__() + "\n"

        return f"Plate: {self.population.plate_x}x{self.population.plate_y}, Connections:\n{conns}"
