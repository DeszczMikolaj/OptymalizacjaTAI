from instance_generator import generate_instance
from genetic_algo import GeneticAlgorithm

if __name__ == '__main__':
    instance = generate_instance(50, 230)
    algo = GeneticAlgorithm(instance, 100, 0.2, 8, 0.2, 0.08)
    best_order, best_fitness_value = algo.solve()

    print(best_fitness_value)