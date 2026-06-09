"""
GA Experiment: Comparing selection, crossover, and mutation operators
for Single Machine Scheduling with Total Weighted Tardiness.

Runs three experiment blocks:
  1. Selection types     (fixed crossover=pmx, mutation=exchange)
  2. Crossover types     (fixed selection=tournament, mutation=exchange)
  3. Mutation types      (fixed selection=tournament, crossover=pmx)

For each configuration:
  - N_RUNS independent runs
  - Tracks best fitness per iteration (convergence curve)
  - Records wall-clock time

Outputs:
  - ga_experiment_results.csv   – raw per-run data
  - ga_experiment_plots.png     – 3×3 grid of plots
"""

import time
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

from genetic_algo  import GeneticAlgorithm
from instance_generator import generate_instance
# Experiment configuration
# ──────────────────────────────────────────────
SEED = 11
N_RUNS = 10          # independent runs per configuration
N_JOBS = 100
MAX_TIME = 230       # generate_instance second argument

GA_BASE = dict(
    population_size=100,
    initial_population_greediness=0.2,
    initial_mutation_level=8,
    tournament_size_ratio=0.2,
    mutation_probability=0.08,
)

SELECTIONS = ["tournament", "linear_rank"]
CROSSOVERS = ["ox", "pmx", "ap"]
MUTATIONS  = ["displacement", "exchange", "scramble", "sim"]

FIXED_SELECTION  = "linear_rank"
FIXED_CROSSOVER  = "pmx"
FIXED_MUTATION   = "displacement"

# ──────────────────────────────────────────────
# Colours / line styles (colour-blind friendly)
# ──────────────────────────────────────────────
PALETTE = [
    "#377eb8", "#e41a1c", "#4daf4a", "#984ea3",
    "#ff7f00", "#a65628", "#f781bf", "#999999",
]
MARKERS  = ["o", "s", "D", "^", "v", "P", "X", "*"]
DASHES   = [
    (None, None),
    (6, 2),
    (3, 2),
    (6, 2, 2, 2),
    (1, 2),
    (8, 2, 2, 2, 2, 2),
]

def style(idx):
    c  = PALETTE[idx % len(PALETTE)]
    m  = MARKERS[idx % len(MARKERS)]
    d  = DASHES[idx % len(DASHES)]
    ls = (0, d) if d[0] is not None else "-"
    return dict(color=c, marker=m, linestyle=ls)


# ──────────────────────────────────────────────
# Core runner
# ──────────────────────────────────────────────
def run_config(label, sel, cx, mut, instance, run_id):
    """Run one GA configuration; returns a dict of metrics."""
    algo = GeneticAlgorithm(
        instance,
        selection_type=sel,
        crossover_type=cx,
        mutation_type=mut,
        **GA_BASE,
    )

    t0 = time.perf_counter()
    best_order, best_fitness, n_generation = algo.solve()
    elapsed = time.perf_counter() - t0

    # collect convergence history (best_fitness_per_iteration must be
    # populated by GeneticAlgorithm.solve(); see note at bottom of file)
    history = getattr(algo, "best_fitness_per_iteration", [best_fitness])

    return dict(
        label=label,
        selection=sel,
        crossover=cx,
        mutation=mut,
        run=run_id,
        best_fitness=best_fitness,
        time_s=elapsed,
        history=history,
        n_iters=n_generation,
    )


def run_block(block_name, configs, instance):
    """
    configs: list of (label, sel, cx, mut)
    Returns list of result dicts.
    """
    results = []
    total = len(configs) * N_RUNS
    done  = 0
    for label, sel, cx, mut in configs:
        for r in range(N_RUNS):
            res = run_config(label, sel, cx, mut, instance, r)
            results.append(res)
            done += 1
            print(f"  [{block_name}] {done}/{total}  {label}  run {r}  "
                  f"fitness={res['best_fitness']:.1f}  t={res['time_s']:.2f}s")
    return results


# ──────────────────────────────────────────────
# Plotting helpers
# ──────────────────────────────────────────────
def convergence_plot(ax, results, title):
    """Mean ± 1 std convergence curves."""
    labels = list(dict.fromkeys(r["label"] for r in results))
    for idx, lbl in enumerate(labels):
        runs = [r["history"] for r in results if r["label"] == lbl]
        max_len = max(len(h) for h in runs)
        padded  = np.array([h + [h[-1]] * (max_len - len(h)) for h in runs],
                           dtype=float)
        mean = padded.mean(axis=0)
        std  = padded.std(axis=0)
        xs   = np.arange(max_len)
        kw   = style(idx)
        step = max(1, max_len // 20)        # draw at most ~20 markers
        ax.plot(xs, mean, label=lbl, markevery=step, markersize=5,
                linewidth=1.8, **kw)
        ax.fill_between(xs, mean - std, mean + std,
                        color=kw["color"], alpha=0.15)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Best fitness")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:,.0f}"))
    ax.legend(fontsize=8, framealpha=0.6)
    ax.grid(True, linewidth=0.4, alpha=0.5)

def n_generations(ax, results, title):
    """Mean ± std number od generations."""
    labels = list(dict.fromkeys(r["label"] for r in results))
    means  = [np.mean([r["n_iters"] for r in results if r["label"] == lbl])
              for lbl in labels]
    stds   = [np.std( [r["n_iters"] for r in results if r["label"] == lbl])
              for lbl in labels]
    xs = np.arange(len(labels))
    bars = ax.bar(xs, means, yerr=stds, capsize=5,
                  color=[PALETTE[i % len(PALETTE)] for i in range(len(labels))],
                  alpha=0.8, edgecolor="white", linewidth=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Number of generations")
    ax.grid(axis="y", linewidth=0.4, alpha=0.5)


def boxplot_fitness(ax, results, title):
    """Box-plot of final best fitness per label."""
    labels  = list(dict.fromkeys(r["label"] for r in results))
    data    = [[r["best_fitness"] for r in results if r["label"] == lbl]
               for lbl in labels]
    bp = ax.boxplot(data, patch_artist=True, notch=False,
                    medianprops=dict(color="black", linewidth=2))
    for patch, idx in zip(bp["boxes"], range(len(labels))):
        patch.set_facecolor(PALETTE[idx % len(PALETTE)])
        patch.set_alpha(0.7)
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Best fitness")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:,.0f}"))
    ax.grid(axis="y", linewidth=0.4, alpha=0.5)


def time_bar(ax, results, title):
    """Mean ± std wall-clock time per label."""
    labels = list(dict.fromkeys(r["label"] for r in results))
    means  = [np.mean([r["time_s"] for r in results if r["label"] == lbl])
              for lbl in labels]
    stds   = [np.std( [r["time_s"] for r in results if r["label"] == lbl])
              for lbl in labels]
    xs = np.arange(len(labels))
    bars = ax.bar(xs, means, yerr=stds, capsize=5,
                  color=[PALETTE[i % len(PALETTE)] for i in range(len(labels))],
                  alpha=0.8, edgecolor="white", linewidth=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Time (s)")
    ax.grid(axis="y", linewidth=0.4, alpha=0.5)


# ──────────────────────────────────────────────
# Summary table
# ──────────────────────────────────────────────
def build_summary(all_results):
    rows = []
    for r in all_results:
        rows.append({
            "block":       r.get("block", ""),
            "label":       r["label"],
            "selection":   r["selection"],
            "crossover":   r["crossover"],
            "mutation":    r["mutation"],
            "run":         r["run"],
            "best_fitness": r["best_fitness"],
            "time_s":      r["time_s"],
            "n_iters":     r["n_iters"],
        })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    rng = np.random.default_rng(SEED)

    print("Generating instance …")
    instance = generate_instance(N_JOBS, MAX_TIME)

    # ── Block 1: selection ──────────────────────
    print("\n=== Block 1: Selection operators ===")
    sel_configs = [
        (s, s, FIXED_CROSSOVER, FIXED_MUTATION)
        for s in SELECTIONS
    ]
    sel_results = run_block("selection", sel_configs, instance)
    for r in sel_results:
        r["block"] = "selection"

    # ── Block 2: crossover ──────────────────────
    print("\n=== Block 2: Crossover operators ===")
    cx_configs = [
        (c, FIXED_SELECTION, c, FIXED_MUTATION)
        for c in CROSSOVERS
    ]
    cx_results = run_block("crossover", cx_configs, instance)
    for r in cx_results:
        r["block"] = "crossover"

    # ── Block 3: mutation ───────────────────────
    print("\n=== Block 3: Mutation operators ===")
    mut_configs = [
        (m, FIXED_SELECTION, FIXED_CROSSOVER, m)
        for m in MUTATIONS
    ]
    mut_results = run_block("mutation", mut_configs, instance)
    for r in mut_results:
        r["block"] = "mutation"

    all_results = sel_results + cx_results + mut_results

    # ── Save CSV ────────────────────────────────
    df = build_summary(all_results)
    csv_path = "ga_experiment_results1.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nResults saved → {csv_path}")

    # ── Print summary stats ─────────────────────
    print("\n── Summary (mean ± std over runs) ──")
    summary = (df.groupby(["block", "label"])
                 .agg(
                     mean_fitness=("best_fitness", "mean"),
                     std_fitness =("best_fitness", "std"),
                     mean_time   =("time_s", "mean"),
                     std_time    =("time_s", "std"),
                 )
                 .round(2))
    print(summary.to_string())

    # ── Plots ───────────────────────────────────
    fig, axes = plt.subplots(3, 3, figsize=(16, 13))
    fig.suptitle(
        f"GA operator comparison  |  {N_JOBS} jobs, {N_RUNS} runs each\n"
        f"(fixed: selection={FIXED_SELECTION}, crossover={FIXED_CROSSOVER}, "
        f"mutation={FIXED_MUTATION}  except the varied block)",
        fontsize=12, y=1.01,
    )

    blocks = [
        ("Selection",  sel_results,  axes[0]),
        ("Crossover",  cx_results,   axes[1]),
        ("Mutation",   mut_results,  axes[2]),
    ]

    for block_name, results, row_axes in blocks:
        n_generations(row_axes[0], results, f"{block_name} – n generations")
        boxplot_fitness (row_axes[1], results, f"{block_name} – fitness distribution")
        time_bar        (row_axes[2], results, f"{block_name} – runtime")

    plt.tight_layout()
    plot_path = "ga_experiment_plots.png"
    fig.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Plots saved → {plot_path}")
    plt.show()


if __name__ == "__main__":
    main()

