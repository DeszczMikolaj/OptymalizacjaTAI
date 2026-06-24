from pathlib import Path

import matplotlib.pyplot as plt

from sa_2c import (
    calculate_weights,
    generator,
    plot_hvi,
    run_hvi_experiment,
    scalarized_value,
    simulated_annealing,
    simulated_annealing_scalarized,
)


def get_setup():
    n_repeats = 100
    iters = [100, 200, 400, 800, 1600]
    n_jobs = 20
    seed_instance = 122
    times, deadlines = generator(n_jobs, seed_instance)
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "wykresy" / f"{seed_instance}"
    output_dir.mkdir(parents=True, exist_ok=True)

    return n_repeats, times, deadlines, n_jobs, iters, output_dir

def run_pareto_2D():
    n_repeats, times, deadlines, n_jobs, iters, output_dir = get_setup()
    results = []

    for i, max_iter in enumerate(iters, start=1):
        seed = i + 333
        fp, p = simulated_annealing(times, deadlines, n_jobs=n_jobs, max_iter=max_iter, seed=seed)
        results.append(fp)

        fig, ax = plt.subplots(figsize=(9, 6))

        ft_all = [obj["total_flowtime"] for _, obj in p]
        mt_all = [obj["max_tardiness"] for _, obj in p]
        ax.scatter(ft_all, mt_all, c="lightgray", s=20, alpha=0.6,
                   label=f"Wszystkie rozwiązania (P)")

        # Front Pareto - posortowany po flowtime, żeby ładnie połączyć linią
        F_sorted = sorted(fp, key=lambda item: item[1]["total_flowtime"])
        ft_front = [obj["total_flowtime"] for _, obj in F_sorted]
        mt_front = [obj["max_tardiness"] for _, obj in F_sorted]

        ax.plot(ft_front, mt_front, c="crimson", linewidth=1.5, linestyle="--",
                zorder=2)
        ax.scatter(ft_front, mt_front, c="crimson", s=60, zorder=3,
                   label=f"Front Pareto (F)", edgecolors="black")

        ax.set_xlabel("Total Flowtime")
        ax.set_ylabel("Max Tardiness")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        fig.savefig(output_dir / f"front_pareto_max_iter_{max_iter}.png")

    fig, ax = plt.subplots(figsize=(9, 6))

    for fp, max_iter in zip(results, iters):
        F_sorted = sorted(fp, key=lambda item: item[1]["total_flowtime"])
        ft_front = [obj["total_flowtime"] for _, obj in F_sorted]
        mt_front = [obj["max_tardiness"] for _, obj in F_sorted]

        ax.plot(ft_front, mt_front, linewidth=1.5, linestyle="--",
                zorder=2)
        ax.scatter(ft_front, mt_front, s=60, zorder=3,
                   label=f"Front Pareto max_iter={max_iter}", edgecolors="black")

    ax.set_xlabel("Total Flowtime")
    ax.set_ylabel("Max Tardiness")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / f"front_pareto_all.png")

def run_hvi():

    n_repeats, times, deadlines, n_jobs, iters, output_dir = get_setup()

    avg_hv, std_hv, ref_point = run_hvi_experiment(
        times, deadlines, n_jobs, iters,
        n_repeats=n_repeats, init_prob=0.97, nadir_factor=1.2
    )

    plot_hvi(iters, avg_hv, output_dir, n_repeats, std_hv)

def run_scalarization(log_to_console=False):
    n_repeats, times, deadlines, n_jobs, iters, output_dir = get_setup()

    parameter_names = ["total_flowtime", "max_tardiness", "max lateness"]
    reference_parameter_name = "total_flowtime"


    fitness_values = []

    for i, max_iter in enumerate(iters, start=1):
        weights = calculate_weights(
            times,
            deadlines,
            n_jobs,
            parameter_names,
            max_iter,
            log_to_console=log_to_console,
            reference_parameter_name=reference_parameter_name,
        )

        seed = i + 333
        on_accept = None

        if log_to_console and max_iter == iters[-1]:
            def on_accept(iteration, solution, obj):
                params = ", ".join(
                    f"{parameter_name}={obj[parameter_name]}"
                    for parameter_name in parameter_names
                )
                fitness = scalarized_value(obj, weights)
                print(
                    f"[SA scalarized accepted] "
                    f"max_iter={max_iter}, "
                    f"it={iteration}, "
                    f"fitness={fitness}, "
                    f"{params}"
                )

        best, accepted_solutions = simulated_annealing_scalarized(
            times,
            deadlines,
            n_jobs=n_jobs,
            weight=weights,
            max_iter=max_iter,
            seed=seed,
            on_accept=on_accept,
        )

        solution, obj = best
        score = scalarized_value(obj, weights)
        fitness_values.append(score)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(iters, fitness_values, marker="o", linewidth=2, color="darkgreen")
    ax.set_xlabel("max_iter")
    ax.set_ylabel("Wartość funkcji dopasowania")
    ax.set_title("Skalaryzowana funkcja dopasowania vs liczba iteracji SA")
    ax.set_xscale("log", base=2)
    ax.set_xticks(iters)
    ax.set_xticklabels(iters)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "scalarized_fitness.png")
    plt.close(fig)



if __name__ == '__main__':
    # run_pareto_2D()
    # run_hvi()
    run_scalarization(True)




