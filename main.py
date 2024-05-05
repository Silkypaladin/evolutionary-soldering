from config import PENALTY_WEIGHTS
from plotter import draw_path
from solution import Solution

if __name__ == '__main__':
    solution = Solution()
    solution.read_solution_from_file('examples/3.txt')
    print(solution)
    solution.population.set_weights(PENALTY_WEIGHTS)
    solution.population.run_genetic_algorithm(5, 10)
    solution.population.sort_population_by_fitness(solution.population.population)
    for i in range(3):
        ind = solution.population.population[i]
        draw_path(ind.genotype, solution.population.plate_x, solution.population.plate_y, solution.start_points)