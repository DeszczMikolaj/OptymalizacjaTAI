
class PSOAlgo:
    def __init__(self):
        self.global_best = None
        self.max_iterations = 10000
        self.max_iterations_without_improvement = 200

        self.inertion = 0.5
        self.local_gravity = 1.75
        self.global_gravity = 1.75



    def solve(self):
        iteration = 0

        particles = self.initilize_population()
        iteration_without_improvement = 0

        while(iteration < self.max_iterations and  iteration <self.max_iterations_without_improvement):

            for

    def.calculate_velocity


    def initilize_population(self):



