from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sa_2c import (
    compute_completion_times,
    calculate_weights,
    evaluate,
    generator,
    next_solution,
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
        fp, p = simulated_annealing(
            times,
            deadlines,
            criteria_names=("total_flowtime", "max_tardiness"),
            n_jobs=n_jobs,
            max_iter=max_iter,
            seed=seed,
        )
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
        times, deadlines, n_jobs, ("total_flowtime", "max_tardiness"), iters,
        n_repeats=n_repeats, init_prob=0.97, nadir_factor=1.2
    )

    plot_hvi(iters, avg_hv, output_dir, n_repeats, std_hv)

def run_scalarization(log_to_console=False):
    n_repeats, times, deadlines, n_jobs, iters, output_dir = get_setup()

    parameter_names = ("total_flowtime", "max_tardiness", "max_lateness")
    reference_parameter_name = "total_flowtime"
    scalarization_repeats = 100


    avg_fitness_values = []
    std_fitness_values = []

    for i, max_iter in enumerate(iters, start=1):
        fitness_values = []

        for rep in range(scalarization_repeats):
            seed = 333 + rep
            should_log_run = log_to_console and max_iter == iters[-1] and rep == 0

            weights = calculate_weights(
                times,
                deadlines,
                n_jobs,
                parameter_names,
                max_iter,
                seed=seed,
                log_to_console=should_log_run,
                reference_parameter_name=reference_parameter_name,
            )

            on_accept = None

            if should_log_run:
                def on_accept(iteration, solution, obj):
                    params = ", ".join(
                        f"{parameter_name}={obj[parameter_name]}"
                        for parameter_name in parameter_names
                    )
                    fitness = scalarized_value(obj, weights)
                    print(
                        f"[SA scalarized accepted] "
                        f"max_iter={max_iter}, "
                        f"rep={rep}, "
                        f"it={iteration}, "
                        f"fitness={fitness}, "
                        f"{params}"
                    )

            best, accepted_solutions = simulated_annealing_scalarized(
                times,
                deadlines,
                parameter_names,
                n_jobs=n_jobs,
                weight=weights,
                max_iter=max_iter,
                seed=seed,
                on_accept=on_accept,
            )

            solution, obj = best
            score = scalarized_value(obj, weights)
            fitness_values.append(score)

        avg_fitness_values.append(float(np.mean(fitness_values)))
        std_fitness_values.append(float(np.std(fitness_values)))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(
        iters,
        avg_fitness_values,
        yerr=std_fitness_values,
        marker="o",
        capsize=4,
        linewidth=2,
        color="darkgreen",
    )
    ax.set_xlabel("max_iter")
    ax.set_ylabel("Średnia wartość funkcji dopasowania")
    ax.set_title(f"Skalaryzowana funkcja dopasowania vs liczba iteracji SA ({scalarization_repeats} przebiegów)")
    ax.set_xscale("log", base=2)
    ax.set_xticks(iters)
    ax.set_xticklabels(iters)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "scalarized_fitness.png")
    plt.close(fig)


def _pareto_4d_plot_data(result, criteria_names):
    points = result["front_points"] + [result["random_point"]]
    labels = [f"Pareto {index}" for index in range(1, len(result["front_points"]) + 1)]
    labels.append("Losowe")
    values = np.array(
        [[obj[criterion] for criterion in criteria_names] for _, obj in points],
        dtype=float,
    )
    return labels, values


def _normalize_by_criterion(values):
    minimums = values.min(axis=0)
    maximums = values.max(axis=0)
    ranges = maximums - minimums
    return np.divide(
        values - minimums,
        ranges,
        out=np.zeros_like(values, dtype=float),
        where=ranges != 0,
    )


def _plot_pareto_4d_bars(labels, values, criteria_names, max_iter, output_dir):
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    axes = np.asarray(axes).ravel()
    colors = ["crimson"] * (len(labels) - 1) + ["steelblue"]

    for ax, criterion, column in zip(axes, criteria_names, values.T):
        ax.bar(labels, column, color=colors, alpha=0.85)
        ax.set_title(criterion)
        ax.tick_params(axis="x", rotation=20)
        ax.grid(True, axis="y", alpha=0.3)

    fig.suptitle(f"Pareto 4D - wykresy slupkowe, max_iter={max_iter}")
    plt.tight_layout()
    fig.savefig(output_dir / f"pareto_4d_bars_{max_iter}.png")
    plt.close(fig)


def _plot_pareto_4d_value_paths(labels, normalized_values, criteria_names, max_iter, output_dir):
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(criteria_names))

    for label, row in zip(labels, normalized_values):
        linestyle = "--" if label == "Losowe" else "-"
        marker = "s" if label == "Losowe" else "o"
        ax.plot(x, row, marker=marker, linewidth=2, linestyle=linestyle, label=label)

    ax.set_xticks(x)
    ax.set_xticklabels(criteria_names, rotation=15)
    ax.set_ylabel("Wartosc znormalizowana (0 = najlepsza w zestawie)")
    ax.set_title(f"Pareto 4D - sciezki wartosci, max_iter={max_iter}")
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    fig.savefig(output_dir / f"pareto_4d_paths_{max_iter}.png")
    plt.close(fig)


def _plot_pareto_4d_scatter(labels, values, normalized_values, criteria_names, max_iter, output_dir):
    row_positions = []
    row_labels = []
    solution_centers = []
    y_position = 0

    for solution_index, label in enumerate(labels):
        group_start = y_position
        for criterion in criteria_names:
            row_positions.append(y_position)
            row_labels.append(criterion)
            y_position += 1
        solution_centers.append((group_start + y_position - 1) / 2)
        y_position += 1

    fig, ax = plt.subplots(figsize=(11, max(6, len(row_positions) * 0.45)))
    colors = ["crimson"] * (len(labels) - 1) + ["steelblue"]

    row_index = 0
    for label, row, raw_row, color, center in zip(
        labels,
        normalized_values,
        values,
        colors,
        solution_centers,
    ):
        ax.text(-0.08, center, label, ha="right", va="center", fontweight="bold")
        for criterion_index, criterion in enumerate(criteria_names):
            y = row_positions[row_index]
            x = row[criterion_index]
            raw_value = raw_row[criterion_index]
            ax.hlines(y, 0, 1, color="gray", linewidth=1, linestyles="dashed", alpha=0.65)
            ax.scatter(x, y, color=color, s=70, edgecolors="black", zorder=3)
            ax.annotate(
                f"{raw_value:.0f}",
                (x, y),
                xytext=(6, 0),
                textcoords="offset points",
                va="center",
                fontsize=8,
            )
            row_index += 1

    ax.set_xlim(-0.18, 1.18)
    ax.set_yticks(row_positions)
    ax.set_yticklabels(row_labels)
    ax.set_xlabel("Wartosc znormalizowana w ramach kryterium (0 = najlepsza, 1 = najgorsza)")
    ax.set_title(f"Pareto 4D - wykres kropkowy, max_iter={max_iter}")
    ax.grid(True, axis="x", alpha=0.25)
    ax.invert_yaxis()

    plt.tight_layout()
    fig.savefig(output_dir / f"pareto_4d_scatter_{max_iter}.png")
    plt.close(fig)


def _plot_pareto_4d_star_coordinates(labels, normalized_values, criteria_names, max_iter, output_dir):
    n_solutions = len(labels)
    n_columns = 2
    n_rows = int(np.ceil(n_solutions / n_columns))
    angles = np.linspace(0, 2 * np.pi, len(criteria_names), endpoint=False)
    anchors = np.column_stack((np.cos(angles), np.sin(angles)))

    fig, axes = plt.subplots(n_rows, n_columns, figsize=(10, 5 * n_rows))
    axes = np.asarray(axes).ravel()
    colors = ["crimson"] * (len(labels) - 1) + ["steelblue"]

    for ax, label, row, color in zip(axes, labels, normalized_values, colors):
        circle = plt.Circle((0, 0), 1, fill=False, color="gray", linewidth=1)
        ax.add_patch(circle)

        for anchor, criterion in zip(anchors, criteria_names):
            ax.plot([0, anchor[0]], [0, anchor[1]], color="gray", linewidth=1, alpha=0.8)
            ax.text(anchor[0] * 1.13, anchor[1] * 1.13, criterion, ha="center", va="center")

        points = row[:, None] * anchors
        polygon = np.vstack((points, points[0]))
        ax.fill(polygon[:, 0], polygon[:, 1], color=color, alpha=0.25)
        ax.plot(polygon[:, 0], polygon[:, 1], color=color, linewidth=2)
        ax.scatter(points[:, 0], points[:, 1], color=color, s=55, edgecolors="black", zorder=3)

        ax.set_title(label)
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.25, 1.25)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")

    for ax in axes[n_solutions:]:
        ax.axis("off")

    fig.suptitle(f"Pareto 4D - wspolrzedne gwiazdowe, max_iter={max_iter}")

    plt.tight_layout()
    fig.savefig(output_dir / f"pareto_4d_star_{max_iter}.png")
    plt.close(fig)


def _plot_pareto_4d_result(result, criteria_names, output_dir):
    plot_dir = output_dir / "pareto_4d"
    plot_dir.mkdir(parents=True, exist_ok=True)

    labels, values = _pareto_4d_plot_data(result, criteria_names)
    normalized_values = _normalize_by_criterion(values)
    max_iter = result["max_iter"]

    _plot_pareto_4d_bars(labels, values, criteria_names, max_iter, plot_dir)
    _plot_pareto_4d_value_paths(labels, normalized_values, criteria_names, max_iter, plot_dir)
    _plot_pareto_4d_scatter(labels, values, normalized_values, criteria_names, max_iter, plot_dir)
    _plot_pareto_4d_star_coordinates(labels, normalized_values, criteria_names, max_iter, plot_dir)


def run_pareto_4D():
    n_repeats, times, deadlines, n_jobs, iters, output_dir = get_setup()
    results = []
    criteria_names = ("total_flowtime", "max_tardiness", "max_lateness", "total_lateness")
    required_front_points = 3

    for i, max_iter in enumerate(iters, start=1):
        seed = i + 54245
        rng = np.random.default_rng(seed)
        front_pareto, pareto = simulated_annealing(
            times,
            deadlines,
            criteria_names=criteria_names,
            n_jobs=n_jobs,
            max_iter=max_iter,
            seed=seed,
        )

        selected_front_points = front_pareto[:required_front_points]
        while len(selected_front_points) < required_front_points:
            base_solution, _ = selected_front_points[-1]
            generated_solution = next_solution(base_solution, rng)
            comp_times = compute_completion_times(times, generated_solution)
            solution_parameters = evaluate(comp_times, deadlines, generated_solution)
            selected_front_points.append((generated_solution[:], solution_parameters))

        random_solution = list(rng.permutation(n_jobs))
        comp_times = compute_completion_times(times, random_solution)
        random_obj = evaluate(comp_times, deadlines, random_solution)

        result = {
            "max_iter": max_iter,
            "front_points": selected_front_points,
            "random_point": (random_solution, random_obj),
        }
        results.append(result)
        _plot_pareto_4d_result(result, criteria_names, output_dir)

    return results





if __name__ == '__main__':
    #run_pareto_2D()
    #run_hvi()
    #run_scalarization(True)
    run_pareto_4D()




