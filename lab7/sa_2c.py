import numpy as np
from RandomNumberGenerator import RandomNumberGenerator
from copy import copy
import matplotlib.pyplot as plt



def generator(n_jobs, seed):
    rng = RandomNumberGenerator(seed)
    p_times = np.zeros((3, n_jobs))
    s = 0
    for i in range(3):
        for j in range(n_jobs):
            time = rng.nextInt(1, 99)
            p_times[i, j] = time
            s += time

    deadlines = np.zeros(n_jobs)
    low = np.floor(s/4)
    high = np.floor(s/2)
    for j in range(n_jobs):
        deadlines[j] = rng.nextInt(low, high)

    return p_times, deadlines


def compute_completion_times(times: np.ndarray, permutation: list[int]) -> np.ndarray:
    n_machines = times.shape[0]
    n_jobs = len(permutation)
    C = np.zeros((n_machines, n_jobs))

    for k in range(n_jobs):
        job = permutation[k]
        for i in range(n_machines):
            proc_time = times[i, job]
            if i == 0 and k == 0:
                C[i, k] = proc_time
            elif i == 0:
                C[i, k] = C[i, k - 1] + proc_time
            elif k == 0:
                C[i, k] = C[i - 1, k] + proc_time
            else:
                C[i, k] = max(C[i - 1, k], C[i, k - 1]) + proc_time

    return C


def total_flowtime(comp_times: np.ndarray) -> int:
    last_machine = comp_times.shape[0] - 1
    return float(np.sum(comp_times[last_machine, :]))


def max_tardiness(comp_times: np.ndarray, deadlines: np.ndarray, permutation: list[int]) -> int:
    last_machine = comp_times.shape[0] - 1
    n_jobs = len(deadlines)

    tardiness = np.zeros(n_jobs)
    for k in range(n_jobs):
        job = permutation[k]
        completion = comp_times[last_machine, k]
        due_date = deadlines[job]
        tardiness[k] = max(0, completion - due_date)

    return np.max(tardiness)



def next_solution(solution):    # generowanie kolejnego rozwiązania z pośród sąsiadów
    new_sol = solution[:]
    i = np.random.randint(low=0, high=len(solution))
    j = np.random.randint(low=0, high=len(solution))
    if i == j:
        j = j - np.random.randint(low=1, high=len(solution) - 1)
    new_sol[i], new_sol[j] = new_sol[j], new_sol[i]
    return new_sol


def evaluate(times, deadlines, solution):
    """Wektor wartości kryteriów dla rozwiązania (oba minimalizujemy)."""
    ft = total_flowtime(times)
    mt = max_tardiness(times, deadlines, solution)
    return (ft, mt)





def dominates(obj1, obj2):
    """
    Czy obj1 dominuje obj2 w sensie Pareto (przy minimalizacji)?
    obj1 dominuje obj2 <=> obj1 nie jest gorszy w żadnym kryterium
                          oraz jest ściśle lepszy w co najmniej jednym.
    """
    not_worse = all(a <= b for a, b in zip(obj1, obj2))
    strictly_better = any(a < b for a, b in zip(obj1, obj2))
    return not_worse and strictly_better


def next_solution(solution):
    # generowanie kolejnego rozwiązania spośród sąsiadów
    new_sol = solution[:]
    i = np.random.randint(low=0, high=len(solution))
    j = np.random.randint(low=0, high=len(solution))
    if i == j:
        j = j - np.random.randint(low=1, high=len(solution) - 1)
    new_sol[i], new_sol[j] = new_sol[j], new_sol[i]
    return new_sol


def acceptance_probability(obj_x, obj_x_prime, it, T0=100.0, alpha=0.97):
    """
    p(it) - prawdopodobieństwo akceptacji rozwiązania x', które nie dominuje x.
    Temperatura maleje geometrycznie wraz z iteracją (chłodzenie).
    Jako miarę pogorszenia 'delta' bierzemy sumę dodatnich różnic
    obu kryteriów (prosta skalaryzacja niezdominowanego pogorszenia).
    """
    T = T0 * (alpha ** it)
    if T <= 1e-12:
        return 0.0
    delta = sum(max(0.0, xp - x) for xp, x in zip(obj_x_prime, obj_x))
    return np.exp(-delta / T)


def pareto_front(P):
    """Wyznacza front Pareto (rozwiązania niezdominowane) ze zbioru P."""
    front = []
    for i, (sol_i, obj_i) in enumerate(P):
        dominated = False
        for j, (sol_j, obj_j) in enumerate(P):
            if i != j and dominates(obj_j, obj_i):
                dominated = True
                break
        if not dominated:
            front.append((sol_i, obj_i))
    return front


def simulated_annealing(times, deadlines, n_jobs, max_iter=1000, init_prob=0.99):


    # 1. P <- pusty zbiór
    P = []

    # 2. it <- 0
    it = 0

    p = init_prob
    # 3. Rozwiązanie początkowe (losowa permutacja zadań)
    x = list(np.random.permutation(n_jobs))
    comp_times = compute_completion_times(times, x)
    obj_x = evaluate(comp_times, deadlines, x)
    # 4. Dodaj x do P
    P.append((x[:], obj_x))

    # 5. Pętla główna
    while it < max_iter - 1:
        # 5.1 Losowy sąsiad x'
        x_prime = next_solution(x)
        comp_times = compute_completion_times(times, x_prime)
        obj_x_prime = evaluate(comp_times, deadlines, x_prime)

        # 5.2 Jeśli x' dominuje x -> zawsze akceptuj
        if dominates(obj_x_prime, obj_x):
            x = x_prime
            obj_x = obj_x_prime
            P.append((x[:], obj_x))
        else:
            # 5.3 W przeciwnym razie akceptuj z prawdopodobieństwem p(it)
            p = p**it
            if np.random.random() < p:
                x = x_prime
                obj_x = obj_x_prime
                P.append((x[:], obj_x))

        # 5.4 it <- it + 1
        it += 1

    # 6. Front Pareto F z P
    F = pareto_front(P)

    return F, P

def hypervolume_2d(front, ref_point):
    """
    Oblicza wskaźnik Hypervolume (HV) dla frontu Pareto w 2D (minimalizacja).
    
    front: lista (rozwiazanie, (f1, f2)) albo lista samych (f1, f2)
    ref_point: punkt referencyjny - nadir (z1, z2)
    """
    points = []
    for item in front:
        obj = item[1] if (isinstance(item, tuple) and len(item) == 2
                           and isinstance(item[1], (tuple, list, np.ndarray))) else item
        points.append(tuple(obj))

    # sortowanie rosnąco po f1 (front niezdominowany => f2 maleje wraz ze wzrostem f1)
    points = sorted(points, key=lambda p: p[0])

    z1, z2 = ref_point
    hv = 0.0
    prev_f2 = z2

    for f1, f2 in points:
        if f1 >= z1 or f2 >= z2:
            continue  # punkt nie wnosi nic do objętości (poza/zdominowany przez nadir)
        width = z1 - f1
        height = prev_f2 - f2
        if height > 0:
            hv += width * height
            prev_f2 = f2

    return hv


def run_hvi_experiment(times, daedlines, n_jobs, max_iters_list, n_repeats=10,
                        init_prob=0.97, nadir_factor=1.2):
  
    all_fronts = {}

    for max_iter in max_iters_list:
        fronts = []
        for rep in range(n_repeats):
            F, P = simulated_annealing(times, daedlines, n_jobs,
                                               max_iter=max_iter, init_prob=init_prob)
            fronts.append(F)
        all_fronts[max_iter] = fronts
        print(f"max_iter={max_iter}: zakończono {n_repeats} powtórzeń")


    worst_f1, worst_f2 = 0.0, 0.0
    for max_iter in max_iters_list:
        for F in all_fronts[max_iter]:
            for _, (f1, f2) in F:
                worst_f1 = max(worst_f1, f1)
                worst_f2 = max(worst_f2, f2)

    ref_point = (worst_f1 * nadir_factor, worst_f2 * nadir_factor)
    print(f"\nPunkt referencyjny (nadir), mnożnik={nadir_factor}: {ref_point}\n")

    avg_hv, std_hv = [], []
    for max_iter in max_iters_list:
        hv_values = [hypervolume_2d(F, ref_point) for F in all_fronts[max_iter]]
        avg_hv.append(np.mean(hv_values))
        std_hv.append(np.std(hv_values))
        print(f"max_iter={max_iter:5d}  HV_avg={np.mean(hv_values):10.2f}  HV_std={np.std(hv_values):8.2f}")

    return avg_hv, std_hv, ref_point

def plot_hvi(max_iters_list, avg_hv, std_hv=None):
    fig, ax = plt.subplots(figsize=(8, 5))

    if std_hv is not None:
        ax.errorbar(max_iters_list, avg_hv, yerr=std_hv, marker='o',
                    capsize=4, linewidth=2, color="steelblue")
    else:
        ax.plot(max_iters_list, avg_hv, marker='o', linewidth=2, color="steelblue")

    ax.set_xlabel("max_iter")
    ax.set_ylabel("Średnia wartość HVI")
    ax.set_title("Hypervolume Indicator vs liczba iteracji SA (10 powtórzeń)")
    ax.set_xscale("log", base=2)
    ax.set_xticks(max_iters_list)
    ax.set_xticklabels(max_iters_list)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(rf"lab7\wykresy\hvi.png")