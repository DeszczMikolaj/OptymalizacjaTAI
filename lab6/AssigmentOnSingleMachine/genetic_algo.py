import math

from models import instance
from models.instance import Instance
import random


class GeneticAlgorithm:
    def __init__(self, instance,  population_size: int, initial_population_greediness: float, initial_mutation_level: int, tournament_size_ratio: float, mutation_probability: float):
        self.instance = instance
        self.best_solution = None
        self.best_objective_value = None
        self.population_size = population_size
        self.initial_population_greediness = initial_population_greediness
        self.initial_mutation_level = initial_mutation_level
        self.tournament_size_ratio = tournament_size_ratio
        self.upgraded_in_current_generation = None
        self.mutation_probability = mutation_probability
        pass

    def solve(self):
        number_of_generations = 0
        number_of_generations_without_improvement = 0

        population = self.initialize_population()

        while self.stop_condition(number_of_generations, number_of_generations_without_improvement):
            self.upgraded_in_current_generation = False

            parents = self.tournament_selection(population)
            children = []
            
            for i in range (0, len(parents), 2):
                child_1, child_2 = self.crossover(parents[i], parents[i+1])
                self.mutation_process(child_1)
                self.mutation_process(child_2)
                children.append(child_1)
                children.append(child_2)

            population = self.select_new_population(population, parents, children)

            number_of_generations += 1
            if not self.upgraded_in_current_generation:
                number_of_generations_without_improvement += 1
            else:
                number_of_generations_without_improvement = 0

        print(f"Search stopped after {number_of_generations} generations")
        return self.best_solution, self.best_objective_value



    def stop_condition(self, number_of_generations: int, number_of_generations_without_improvement: int):
        return number_of_generations_without_improvement < 500 and number_of_generations < 10000


    def initialize_population(self):
        population = []
        size_of_instance = len(self.instance.jobs)

        greedy_population_size = math.floor(self.population_size * self.initial_population_greediness)
        random_population_size = self.population_size - greedy_population_size

        for i in range(random_population_size):
            individual = random.sample(range(size_of_instance), size_of_instance)
            self.update_if_best(individual)
            population.append(individual)
        pass

        greediest_individual_blueprint = self.generate_greedy_solution()

        for i in range(greedy_population_size):
            greedy_individual =  greediest_individual_blueprint.copy()
            for j in range(self.initial_mutation_level):
                self.mutate(greedy_individual)
            self.update_if_best(greedy_individual)
            population.append(greedy_individual)

        return population

    def generate_greedy_solution(self):
        jobs_sorted = sorted(self.instance.jobs, key=lambda job: job.weight / job.duration, reverse=True)
        order = [job.index for job in jobs_sorted]
        return order

    # Zamiana losowych dwóch sąsiadujących elementów
    def mutate(self, greedy_individual):
        instance_size = len(greedy_individual)
        random_index = random.randint(0, instance_size - 1)
        next_index  = (random_index + 1) % instance_size
        greedy_individual[random_index], greedy_individual[next_index] = greedy_individual[next_index], greedy_individual[random_index]
        return greedy_individual


    def crossover(self, parent_1, parent_2):
        instance_size = len(parent_1)

        stable_part = math.floor(instance_size / 2)

        child_1 = parent_1[:stable_part]

        for i in range(instance_size):
            if parent_2[i] not in child_1:
                child_1.append(parent_2[i])

        self.update_if_best(child_1)

        child_2 = parent_2[:stable_part]

        for i in range(instance_size):
            if parent_1[i] not in child_2:
                child_2.append(parent_1[i])

        self.update_if_best(child_2)

        return child_1, child_2

    def fitness_function(self, individual):
        elapsed_time = 0
        total_delay = 0

        for i in range(len(individual)):
            job = self.instance.jobs[individual[i]]
            elapsed_time += job.duration
            delay = job.deadline - elapsed_time
            if delay > 0:
                total_delay += delay * job.weight

        return total_delay

    def tournament_selection(self, population):
        selected_parents = []
        tournament_size = math.floor(len(population) * self.tournament_size_ratio)
        number_of_parents = math.floor(len(population) / 2) * 2

        for i in range(number_of_parents):
            tournament_participants = []
            for j in range(tournament_size):
                tournament_participants.append(random.choice(population))
            selected_parents.append(min(tournament_participants, key=lambda individual: self.fitness_function(individual)))

        return selected_parents

    def update_if_best(self, individual):
        fitness = self.fitness_function(individual)
        if self.best_objective_value is None or fitness < self.best_objective_value :
            self.best_objective_value = fitness
            self.best_solution = individual
            self.upgraded_in_current_generation = True

    def mutation_process(self, individual):
        if random.random() < self.mutation_probability:
            self.mutate(individual)
            self.update_if_best(individual)

    def select_new_population(self, population, parents, children):
        return children
