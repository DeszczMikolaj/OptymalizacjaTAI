from docplex.mp.model import Model
from RandomNumberGenerator import RandomNumberGenerator
import numpy as np

rng = RandomNumberGenerator(222)


def generator(matrix_size):
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



m = Model()
n = 9
flow_values, dist_values = generator(n)

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
print(m.number_of_variables)
details = m.solve_details

if solution:
    assignment = []
    for i in range(n):
        for k in range(n):
            if x[i][k].solution_value == 1:
                assignment.append(k)
                break
    print("Lokalizacje przypisane kolejnym zakładom: ", assignment)
    print(details.deterministic_time)