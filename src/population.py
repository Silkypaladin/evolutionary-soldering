import copy
import csv
import random
from enum import Enum

from connection import Connection
from individual import Individual
from config import *
from statistics import mean, stdev
import math


class SelectionMode(Enum):
    TOURNAMENT = 1
    ROULETTE = 2


class Population:
    def __init__(self, plate_x=0, plate_y=0, filename='results', selection_mode=SelectionMode.ROULETTE):
        self.plate_x = plate_x
        self.plate_y = plate_y
        self.connections: list[Connection] = list()
        self.population: list[Individual] = list()
        self.weights: dict[str, int] = dict()
        self.filename = filename + '.csv'
        self.selection_mode = selection_mode

    def set_weights(self, weights) -> None:
        self.weights = weights

    def generate_population(self, individuals_num: int) -> None:
        for i in range(individuals_num):
            next_ind = Individual()
            next_ind.generate_genotype(self.connections, self.plate_x, self.plate_y)
            self.population.append(next_ind)

    @staticmethod
    def cross_two_individuals(ind_one: Individual, ind_two: Individual) -> (Individual, Individual):
        gene_swap_index = random.randrange(1, len(ind_one.genotype))
        cross_prob = random.uniform(0, 1)

        if cross_prob >= 1 - CROSS_PROBABILITY:
            child_one = Individual()
            child_two = Individual()
            for i in range(gene_swap_index):
                child_one.genotype.append(copy.deepcopy(ind_one.genotype[i]))
                child_two.genotype.append(copy.deepcopy(ind_two.genotype[i]))
            for j in range(gene_swap_index, len(ind_one.genotype)):
                child_one.genotype.append(copy.deepcopy(ind_two.genotype[j]))
                child_two.genotype.append(copy.deepcopy(ind_one.genotype[j]))
        else:
            child_one = copy.deepcopy(ind_one)
            child_two = copy.deepcopy(ind_two)

        return child_one, child_two

    def roulette_selection(self) -> [Individual, Individual]:
        fitness_total = 0
        probabilities = []
        fitness_values = []
        for individual in self.population:
            fitness_values.append(individual.fitness)
            fitness_total += individual.fitness

        for i in range(len(self.population)):
            probabilities.append((1 / fitness_values[i]) / fitness_total)

        parent_one = random.choices(self.population, probabilities)[0]
        parent_two = random.choices(self.population, probabilities)[0]

        while parent_one is parent_two:
            parent_one = random.choices(self.population, probabilities)[0]

        return [parent_one, parent_two]

    def tournament_selection(self, group_size: int) -> [Individual, Individual]:
        candidates = []
        for i in range(group_size):
            candidate = random.choice(self.population)
            while candidate in candidates:
                candidate = random.choice(self.population)
            candidates.append(candidate)

        candidates = self.sort_population_by_fitness(candidates)

        best_cand_one = candidates[0]
        best_cand_two = candidates[1]
        return [best_cand_one, best_cand_two]

    def sort_population_by_fitness(self, population: list[Individual]) -> list[Individual]:
        for individual in population:
            current_penalty = individual.calculate_total_individual_penalty(self.connections, self.weights, self.plate_x, self.plate_y)
            individual.fitness = current_penalty
        population.sort(key=lambda x: x.fitness)
        return population

    def sort_population_by_fitness_static(self, population: list[Individual]) -> list[Individual]:
        for individual in population:
            current_penalty = individual.get_total_individual_penalty_no_adaptation(self.connections, self.weights, self.plate_x, self.plate_y)
            individual.static_fitness = current_penalty
        return population

    @staticmethod
    def update_connection_weights(connections_crossed):
        for c in connections_crossed:
            c.weight += 1

    def run_genetic_algorithm(self, iterations: int, individuals_num: int) -> None:
        self.generate_population(individuals_num)
        last_best_fitness = math.inf
        with open(self.filename, mode='a') as results_file:
            header = ['iteration', 'best', 'worst', 'avg', 'std']
            writer = csv.writer(results_file, delimiter=';', lineterminator='\n')
            writer.writerow(header)
            for i in range(iterations):
                self.sort_population_by_fitness(self.population)
                self.sort_population_by_fitness_static(self.population)
                result = self.get_static_results()
                result = [i] + result
                writer.writerow(result)
                best = self.population[0]
                next_population = [best]
                if last_best_fitness <= best.fitness:
                    Population.update_connection_weights(best.crossing_connections)
                last_best_fitness = best.fitness
                while len(next_population) < individuals_num:
                    if self.selection_mode == SelectionMode.TOURNAMENT:
                        parents = self.tournament_selection(TOURNAMENT_SIZE)
                    else:
                        parents = self.roulette_selection()
                    children = self.cross_two_individuals(parents[0], parents[1])
                    children[0].mutate_individual(self.plate_x, self.plate_y)
                    next_population.append(children[0])
                    children[1].mutate_individual(self.plate_x, self.plate_y)
                    next_population.append(children[1])
                if len(next_population) > individuals_num:
                    next_population.pop()
                self.population = next_population[:]
            self.sort_population_by_fitness_static(self.population)
            writer.writerow(header)
            static = self.get_static_results()
            writer.writerow(static)
            writer.writerow(['---', '---', '---', '---', '---'])

    def test_naive_method(self, individuals_num: int, filename: str) -> None:
        self.generate_population(individuals_num)
        with open(filename, mode='a') as results_file:
            header = ['iteration', 'best', 'worst', 'avg', 'std']
            writer = csv.writer(results_file, delimiter=';', lineterminator='\n')
            writer.writerow(header)
            self.population = self.sort_population_by_fitness_static(self.population)
            result = self.get_static_results()
            writer.writerow(result)

    def find_test_run_results(self) -> list[int]:
        result = []
        fitness_list = []
        for individual in self.population:
            fitness_list.append(individual.fitness)
        # Best
        result.append(self.population[0].fitness)
        # Worst
        result.append(self.population[len(self.population) - 1].fitness)
        # Avg
        result.append(mean(fitness_list))
        # Std Dev
        result.append(stdev(fitness_list))

        return result

    def get_static_results(self) -> list[int]:
        result = []
        fitness_list = []
        for individual in self.population:
            fitness_list.append(individual.static_fitness)
        # Best
        result.append(self.population[0].static_fitness)
        # Worst
        result.append(max(fitness_list))
        # Avg
        result.append(mean(fitness_list))
        # Std Dev
        result.append(stdev(fitness_list))
        return result
