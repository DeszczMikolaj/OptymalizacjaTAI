import numpy as np
from RandomNumberGenerator import RandomNumberGenerator
import matplotlib.pyplot as plt


OBJECTIVE_KEYS = ("total_flowtime", "max_tardiness")


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
    # Czas ukończenia każdego z zadań na każdej maszynie
    C = np.zeros((n_machines, n_jobs))

    for k in range(n_jobs):
        job = permutation[k]
        for i in range(n_machines):
            proc_time = times[i, job]
            # Pierwsze zadanie kończy się na pierwszej maszynie bez warunkowo
            if i == 0 and k == 0:
                C[i, k] = proc_time
            # Jeżeli kolejne zadanie jest wykonywane na pierwszej maszynie, dodajemy czas zadania do czasu
            #   zakończenia poprzedniego zadania
            elif i == 0:
                C[i, k] = C[i, k - 1] + proc_time
            # Jeżeli pierwsze zadania na kolejnej maszynie, czas zakończenia zadania dodajemy
            #   do czasu zakończenia tego samego zadania na poprzedniej maszynie
            elif k == 0:
                C[i, k] = C[i - 1, k] + proc_time
            # Jeżeli kolejne zadanie na kolejnej maszynie to dodajemy czas zadania do czasu ukończenia poprzedniego zadania,
            #   pod warunkiem, że dane zadanie zdążyło się zakończyć na poprzedniej maszynie
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


def max_lateness(comp_times: np.ndarray, deadlines: np.ndarray, permutation: list[int]) -> int:
    last_machine = comp_times.shape[0] - 1
    n_jobs = len(deadlines)

    tardiness = np.zeros(n_jobs)
    for k in range(n_jobs):
        job = permutation[k]
        completion = comp_times[last_machine, k]
        due_date = deadlines[job]
        tardiness[k] = completion - due_date

    return np.max(tardiness)


def evaluate(times, deadlines, solution):
    """Wektor wartości kryteriów dla rozwiązania (oba minimalizujemy)."""
    ft = total_flowtime(times)
    mt = max_tardiness(times, deadlines, solution)
    ml = max_lateness(times, deadlines, solution)

    return {
        "total_flowtime": ft,
        "max_tardiness": mt,
        "max lateness": ml
    }


def objective_values(obj):
    return tuple(obj[key] for key in OBJECTIVE_KEYS)


def dominates(obj1, obj2):
    """
    Czy obj1 dominuje obj2 w sensie Pareto (przy minimalizacji)?
    obj1 dominuje obj2 <=> obj1 nie jest gorszy w żadnym kryterium
                          oraz jest ściśle lepszy w co najmniej jednym.
    """

    objective_keys_used = ("total_flowtime", "max_tardiness")

    not_worse = all(obj1[key] <= obj2[key] for key in objective_keys_used)
    strictly_better = any(obj1[key] < obj2[key] for key in objective_keys_used)
    return not_worse and strictly_better


def geometric_acceptance_probability(init_prob, it):
    return init_prob ** it


def accept_pareto_solution(obj_x, obj_x_candidate, it, rng, init_prob):
    if dominates(obj_x_candidate, obj_x):
        return True

    p = geometric_acceptance_probability(init_prob, it)
    return rng.random() < p


def scalarized_value(obj, weight):
    return sum(obj[key] * value for key, value in weight.items())


class ScalarizedAcceptance:
    def __init__(self, weight):
        self.weight = dict(weight)

    def __call__(self, obj_x, obj_x_candidate, it, rng, init_prob):
        current_value = scalarized_value(obj_x, self.weight)
        candidate_value = scalarized_value(obj_x_candidate, self.weight)

        if candidate_value <= current_value:
            return True

        p = geometric_acceptance_probability(init_prob, it)
        return rng.random() < p


def make_scalarized_acceptance(weight):
    return ScalarizedAcceptance(weight)

class SingleParameterAcceptance:
    def __init__(self, parameter_name):
        self.parameter_method = parameter_name

    def __call__(self, obj_x, obj_x_candidate, it, rng, init_prob):
        current_value = obj_x[self.parameter_method]
        candidate_value = obj_x_candidate[self.parameter_method]

        if candidate_value <= current_value:
            return True

        p = geometric_acceptance_probability(init_prob, it)
        return rng.random() < p


def make_single_parameter_acceptance(parameter_method):
    return SingleParameterAcceptance(parameter_method)


def next_solution(solution, rng):
    # generowanie kolejnego rozwiązania spośród sąsiadów
    new_sol = solution[:]
    i = rng.integers(low=0, high=len(solution))
    j = rng.integers(low=0, high=len(solution))
    if i == j:
        j = j - rng.integers(low=1, high=len(solution) - 1)
    new_sol[i], new_sol[j] = new_sol[j], new_sol[i]
    return new_sol


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


def simulated_annealing(times, deadlines, n_jobs, max_iter=1000, init_prob=0.95, seed=None,
                        acceptance_rule=None, on_accept=None):
    rng = np.random.default_rng(seed)
    if acceptance_rule is None:
        acceptance_rule = accept_pareto_solution

    P = []

    it = 1

    # Rozwiązanie początkowe (losowa permutacja zadań)
    x = list(rng.permutation(n_jobs))
    comp_times = compute_completion_times(times, x)
    obj_x = evaluate(comp_times, deadlines, x)
    P.append((x[:], obj_x))

    while it <= max_iter :

        x_prime = next_solution(x, rng)
        comp_times = compute_completion_times(times, x_prime)
        obj_x_candidate = evaluate(comp_times, deadlines, x_prime)

        if acceptance_rule(obj_x, obj_x_candidate, it, rng, init_prob):
            x = x_prime
            obj_x = obj_x_candidate
            P.append((x[:], obj_x))
            if on_accept is not None:
                on_accept(it, x[:], obj_x)

        # 5.4 it <- it + 1
        it += 1

    # 6. Front Pareto F z P
    F = pareto_front(P)

    return F, P


def simulated_annealing_scalarized(times, deadlines, n_jobs, weight, max_iter=1000,
                                   init_prob=0.95, seed=None, on_accept=None):
    acceptance_rule = make_scalarized_acceptance(weight)
    _, P = simulated_annealing(
        times,
        deadlines,
        n_jobs,
        max_iter=max_iter,
        init_prob=init_prob,
        seed=seed,
        acceptance_rule=acceptance_rule,
        on_accept=on_accept,
    )
    best = min(P, key=lambda item: scalarized_value(item[1], weight))
    return best, P


def calculate_weights(times, deadlines, n_jobs, parameters_names, max_iterations=1000,
                      init_prob=0.95, seed=333, log_to_console=False,
                      reference_parameter_name=None):
    optimal_parameters = {}

    for index, parameter_name in enumerate(parameters_names):
        acceptance_rule = make_single_parameter_acceptance(parameter_name)
        _, accepted_solutions = simulated_annealing(
            times,
            deadlines,
            n_jobs,
            max_iter=max_iterations,
            init_prob=init_prob,
            seed=seed + index,
            acceptance_rule=acceptance_rule,
        )
        best_solution, best_obj = min(
            accepted_solutions,
            key=lambda item: item[1][parameter_name],
        )
        optimal_parameters[parameter_name] = {
            "value": best_obj[parameter_name],
            "objectives": best_obj,
            "solution": best_solution,
        }

    parameter_deltas = {}

    for parameter_name in parameters_names:
        best_value = optimal_parameters[parameter_name]["value"]
        other_optimization_values = [
            optimal_parameters[optimized_parameter]["objectives"][parameter_name]
            for optimized_parameter in parameters_names
            if optimized_parameter != parameter_name
        ]

        worst_value = max(other_optimization_values)
        parameter_deltas[parameter_name] = {
            "best": best_value,
            "worst": worst_value,
            "delta": worst_value - best_value,
        }

    weight = {}
    for parameter_name, delta_info in parameter_deltas.items():
        delta = delta_info["delta"]
        if delta == 0:
            raise ValueError(f"Nie mozna wyznaczyc wagi dla {parameter_name}: delta wynosi 0.")
        weight[parameter_name] = 1 / delta

    if reference_parameter_name is not None:
        if not isinstance(reference_parameter_name, str):
            raise TypeError("Kryterium referencyjne musi byc pojedyncza nazwa parametru jako string.")
        if reference_parameter_name not in weight:
            raise ValueError(f"Nieznane kryterium referencyjne: {reference_parameter_name}.")
        scale = 1 / weight[reference_parameter_name]
        weight = {
            parameter_name: parameter_weight * scale
            for parameter_name, parameter_weight in weight.items()
        }

    if log_to_console:
        print(f"\n[Skalaryzacja] max_iter={max_iterations}")
        for parameter_name in parameters_names:
            delta_info = parameter_deltas[parameter_name]
            print(
                f"  {parameter_name}: "
                f"min={delta_info['best']}, "
                f"max={delta_info['worst']}, "
                f"delta={delta_info['delta']}, "
                f"weight={weight[parameter_name]}"
            )

    return weight


def hypervolume_2d(front, ref_point):
    """
    Oblicza wskaźnik Hypervolume (HV) dla frontu Pareto w 2D (minimalizacja).
    
    front: lista (rozwiazanie, obj), gdzie obj jest dict z kluczami OBJECTIVE_KEYS
    ref_point: punkt referencyjny - nadir (z1, z2)
    """
    points = [
        (obj["total_flowtime"], obj["max_tardiness"])
        for _, obj in front
    ]

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


def run_hvi_experiment(times, deadlines, n_jobs, max_iters_list, n_repeats=10,
                        init_prob=0.97, nadir_factor=1.2):
  
    all_fronts = {}

    for max_iter in max_iters_list:
        fronts = []
        for rep in range(n_repeats):
            F, P = simulated_annealing(times, deadlines, n_jobs,
                                               max_iter=max_iter, init_prob=init_prob, seed=rep+333)
            fronts.append(F)
        all_fronts[max_iter] = fronts
        print(f"max_iter={max_iter}: zakończono {n_repeats} powtórzeń")


    worst_f1, worst_f2 = 0.0, 0.0
    for max_iter in max_iters_list:
        for F in all_fronts[max_iter]:
            for _, obj in F:
                f1 = obj["total_flowtime"]
                f2 = obj["max_tardiness"]
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

def plot_hvi(max_iters_list, avg_hv, output_dir,n_repeats, std_hv=None):
    fig, ax = plt.subplots(figsize=(8, 5))

    if std_hv is not None:
        ax.errorbar(max_iters_list, avg_hv, yerr=std_hv, marker='o',
                    capsize=4, linewidth=2, color="steelblue")
    else:
        ax.plot(max_iters_list, avg_hv, marker='o', linewidth=2, color="steelblue")

    ax.set_xlabel("max_iter")
    ax.set_ylabel("Średnia wartość HVI")
    ax.set_title(f"Hypervolume Indicator vs liczba iteracji SA ({n_repeats} powtórzeń)")
    ax.set_xscale("log", base=2)
    ax.set_xticks(max_iters_list)
    ax.set_xticklabels(max_iters_list)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir/"hvi.png")
    plt.close(fig)
