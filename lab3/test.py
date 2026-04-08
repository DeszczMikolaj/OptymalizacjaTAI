from docplex.mp.model import Model
from RandomNumberGenerator import RandomNumberGenerator 

rng = RandomNumberGenerator(222)


def generator(matrix_size):
    flow_values = []
    for i in range(matrix_size):
        flow_values.append([])
        for j in range(matrix_size):
            if i != j:
                flow_values[i].append(rng.nextInt(low=1, high=50))
            else:
                flow_values[i].append(0)
    dist_values = []
    for i in range(matrix_size):
        dist_values.append([])
        for j in range(matrix_size):
            if i != j:
                dist_values[i].append(rng.nextInt(low=1, high=50))
            else:
                dist_values[i].append(0)
    
    return flow_values, dist_values




m = Model()
n = 8
flow_values, dist_values = generator(n)
x = []
for i in range(n):
    x.append(m.integer_var())

m.minimize(m.sum())