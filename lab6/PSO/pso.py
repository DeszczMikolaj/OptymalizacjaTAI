from dataclasses import dataclass, field
import random
import math

@dataclass
class Particle:
    position: list[float]
    velocity: list[float]
    local_memory: list[float]          # najlepsza pozycja zapamiętana przez cząstkę
    local_memory_value: float = float("inf")   # wartość f w local_memory



def objective_function(position: list[float]) -> float:

   #  return sum(x ** 2 for x in position)

class PSOAlgo:
    def __init__(self):

        self.max_iterations = 10_000
        self.max_iterations_without_improvement = 200

        self.inertia = 0.5          # ω  – tłumienie prędkości
        self.local_gravity = 1.75   # φl – przyciąganie do lokalnego optimum
        self.global_gravity = 1.75  # φg – przyciąganie do globalnego optimum
        self.learning_rate = 0.9    # c  – tempo uczenia (skaluje krok pozycji)

        self.n_dimensions = 2                        # liczba zmiennych
        self.lower_bounds = [-5.0] * self.n_dimensions
        self.upper_bounds = [ 5.0] * self.n_dimensions

        self.swarm_size = 30

        self.global_best: list[float] | None = None
        self.global_best_value: float = float("inf")
        self.swarm: list[Particle] = []


    def _random_position(self) -> list[float]:
        return [
            random.uniform(self.lower_bounds[i], self.upper_bounds[i])
            for i in range(self.n_dimensions)
        ]

    def _random_velocity(self) -> list[float]:
        return [
            random.uniform(
                self.lower_bounds[i] - self.upper_bounds[i],
                self.upper_bounds[i] - self.lower_bounds[i],
            )
            for i in range(self.n_dimensions)
        ]

    def _init_swarm(self) -> None:
        self.swarm = []
        for _ in range(self.swarm_size):
            pos = self._random_position()
            vel = self._random_velocity()
            value = objective_function(pos)

            particle = Particle(
                position=pos[:],
                velocity=vel[:],
                local_memory=pos[:],
                local_memory_value=value,
            )
            self.swarm.append(particle)

            if value < self.global_best_value:
                self.global_best_value = value
                self.global_best = pos[:]

    # ── krok prędkości i pozycji ──────────────────────────────────────────────

    def _update_particle(self, particle: Particle) -> None:
        for i in range(self.n_dimensions):
            r_l = random.random()   # losowość składnika lokalnego
            r_g = random.random()   # losowość składnika globalnego

            # wzór z instrukcji:  v ← ω·v + φl·rl·(l - x) + φg·rg·(g - x)
            particle.velocity[i] = (
                self.inertia * particle.velocity[i]
                + self.local_gravity  * r_l * (particle.local_memory[i] - particle.position[i])
                + self.global_gravity * r_g * (self.global_best[i]       - particle.position[i])
            )

            # x ← x + c·v
            particle.position[i] += self.learning_rate * particle.velocity[i]

            # opcjonalne: odbicie od granic zamiast obcinania
            particle.position[i] = max(self.lower_bounds[i],
                                       min(self.upper_bounds[i], particle.position[i]))

    def _update_memories(self, particle: Particle) -> None:
        value = objective_function(particle.position)

        if value < particle.local_memory_value:
            particle.local_memory = particle.position[:]
            particle.local_memory_value = value

            if value < self.global_best_value:
                self.global_best_value = value
                self.global_best = particle.position[:]

    # ── główna pętla ──────────────────────────────────────────────────────────

    def run(self) -> tuple[list[float], float]:
        """
        Uruchamia algorytm PSO.

        Zwraca:
            (najlepsza_pozycja, wartość_funkcji_celu)
        """
        self._init_swarm()

        iterations_without_improvement = 0
        prev_best = self.global_best_value

        for iteration in range(1, self.max_iterations + 1):
            for particle in self.swarm:
                self._update_particle(particle)
                self._update_memories(particle)

            # sprawdzenie warunku stopu (brak poprawy)
            if self.global_best_value < prev_best:
                iterations_without_improvement = 0
                prev_best = self.global_best_value
            else:
                iterations_without_improvement += 1

            if iterations_without_improvement >= self.max_iterations_without_improvement:
                print(f"[PSO] Zatrzymano po {iteration} iteracjach (brak poprawy).")
                break

            # opcjonalny log co 500 iteracji
            if iteration % 500 == 0:
                print(f"  iter {iteration:6d} | best = {self.global_best_value:.6f}")

        print(f"\n[PSO] Wynik końcowy: f = {self.global_best_value:.8f}")
        print(f"[PSO] Pozycja:       {[round(x, 6) for x in self.global_best]}")
        return self.global_best, self.global_best_value


# ──────────────────────────────────────────────
#  Punkt wejścia
# ──────────────────────────────────────────────

if __name__ == "__main__":
    pso = PSOAlgo()

    # Dostosuj parametry przed uruchomieniem:
    # pso.n_dimensions = 5
    # pso.lower_bounds = [-10.0] * pso.n_dimensions
    # pso.upper_bounds = [ 10.0] * pso.n_dimensions
    # pso.swarm_size   = 50
    # pso.inertia      = 0.7

    best_position, best_value = pso.run()
