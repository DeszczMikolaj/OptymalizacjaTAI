from docplex.mp.model import Model
from RandomNumberGenerator import RandomNumberGenerator
import numpy as np




def generator(matrix_size, seed):
    rng = RandomNumberGenerator(seed)
    flow_values = np.zeros((matrix_size, matrix_size))
    for i in range(matrix_size):
        for j in range(i, matrix_size):
            if i != j:
                flow_values[i, j] = rng.nextInt(low=1, high=50)
                flow_values[j, i] = flow_values[i, j]
    dist_values = np.zeros((matrix_size, matrix_size))
    for i in range(matrix_size):
        for j in range(i, matrix_size):
            if i != j:
                dist_values[i, j] = rng.nextInt(low=1, high=50)
                dist_values[j, i] = dist_values[i, j]

    
    return flow_values, dist_values

times = np.zeros((7, 50))

for row, n in enumerate(range(3, 10)):
    for col in range(50):
        m = Model()
        flow_values, dist_values = generator(n, col)

        x = [[m.binary_var(name=f"x_{i}_{k}") for k in range(n)] for i in range(n)]

        for i in range(n):
            m.add_constraint(m.sum(x[i][k] for k in range(n)) == 1)

        for k in range(n):
            m.add_constraint(m.sum(x[i][k] for i in range(n)) == 1)


        obj_terms = []
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    for l in range(n):
                        if flow_values[i][j] != 0:
                            obj_terms.append(flow_values[i][j] * dist_values[k][l] * x[i][k] * x[j][l])

        m.minimize(m.sum(obj_terms))
        solution = m.solve()
        details = m.solve_details

        if solution:
            times[row, col] = details.deterministic_time
        else:
            print("Solution not found")

np.save("ticks_data", times)