from sa_2c import simulated_annealing, generator, run_hvi_experiment, plot_hvi
import matplotlib.pyplot as plt



if __name__ == '__main__':
    iters = [100, 200, 400, 800, 1600]
    n_jobs = 20
    times, deadlines = generator(n_jobs, 123)

    results = []
    for max_iter in iters:
        fp, p = simulated_annealing(times, deadlines, n_jobs=n_jobs, max_iter=max_iter)
        results.append(fp)

        
    
        fig, ax = plt.subplots(figsize=(9, 6))

        ft_all = [obj[0] for _, obj in p]
        mt_all = [obj[1] for _, obj in p]
        ax.scatter(ft_all, mt_all, c="lightgray", s=20, alpha=0.6,
                    label=f"Wszystkie rozwiązania (P)")

        # Front Pareto - posortowany po flowtime, żeby ładnie połączyć linią
        F_sorted = sorted(fp, key=lambda item: item[1][0])
        ft_front = [obj[0] for _, obj in F_sorted]
        mt_front = [obj[1] for _, obj in F_sorted]

        ax.plot(ft_front, mt_front, c="crimson", linewidth=1.5, linestyle="--",
                zorder=2)
        ax.scatter(ft_front, mt_front, c="crimson", s=60, zorder=3,
                label=f"Front Pareto (F)", edgecolors="black")

        ax.set_xlabel("Total Flowtime")
        ax.set_ylabel("Max Tardiness")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        fig.savefig(rf"lab7\wykresy\front_pareto_max_iter_{max_iter}.png")

    fig, ax = plt.subplots(figsize=(9, 6))

    for fp, max_iter in zip(results, iters):
        F_sorted = sorted(fp, key=lambda item: item[1][0])
        ft_front = [obj[0] for _, obj in F_sorted]
        mt_front = [obj[1] for _, obj in F_sorted]

        ax.plot(ft_front, mt_front, linewidth=1.5, linestyle="--",
                zorder=2)
        ax.scatter(ft_front, mt_front,  s=60, zorder=3,
                label=f"Front Pareto max_iter={max_iter}", edgecolors="black")

    ax.set_xlabel("Total Flowtime")
    ax.set_ylabel("Max Tardiness")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(rf"lab7\wykresy\front_pareto_all.png")


        
    avg_hv, std_hv, ref_point = run_hvi_experiment(
        times, deadlines, n_jobs, iters,
        n_repeats=10, init_prob=0.97, nadir_factor=1.2
    )

    plot_hvi(iters, avg_hv, std_hv)