import numpy as np
import matplotlib.pyplot as plt

data = np.load("ticks_data.npy")
avg_times = []
size = [3, 4, 5, 6, 7, 8, 9]

for row in data:
    avg_times.append(np.mean(row))

fig, ax = plt.subplots()
ax.scatter(size, avg_times)
plt.xlabel("rozmiar problemu")
plt.ylabel("czas")
plt.show()