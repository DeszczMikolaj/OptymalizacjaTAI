from __future__ import annotations

import heapq
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional


class Node(ABC):
    @abstractmethod
    def is_complete(self) -> bool:
        """Czy węzeł reprezentuje kompletne (a nie częściowe) rozwiązanie?"""
        ...

    @abstractmethod
    def bound(self) -> float:
        """
        Ograniczenie górne wartości obiektywnej osiągalnej z tego węzła
        (przy maksymalizacji). Przy minimalizacji zwróć ograniczenie dolne
        i odpowiednio dostosuj porównania w BranchAndBound.
        """
        ...

    @abstractmethod
    def value(self) -> float:
        """Wartość obiektywna węzła (sensowna tylko dla kompletnych węzłów)."""
        ...

    @abstractmethod
    def branch(self) -> List["Node"]:
        """Podzial węzła"""
        ...

    # Potrzebne do kopca priorytetowego (maksymalizacja → odwracamy znak)
    def __lt__(self, other: "Node") -> bool:
        return self.bound() > other.bound()



class BranchAndBound:


    def __init__(self, maximize: bool = True) -> None:
        self.maximize = maximize
        self.best_value: float = float("-inf") if maximize else float("inf")
        self.best_node: Optional[Node] = None
        self.nodes_explored: int = 0

    # ----------------------------------------------------------
    def solve(self, root: Node) -> Optional[Node]:
        """
        Zwraca najlepszy znaleziony węzeł (kompletne rozwiązanie)
        lub None, jeśli żadnego nie znaleziono.
        """
        heap: List[Node] = [root]

        while heap:
            node = heapq.heappop(heap)
            self.nodes_explored += 1

            # Odcinanie (pruning)
            if self.maximize:
                if node.bound() <= self.best_value:
                    continue          # nie możemy poprawić najlepszego wyniku
            else:
                if node.bound() >= self.best_value:
                    continue

            # --- Sprawdzenie kompletności ---
            if node.is_complete():
                val = node.value()
                if self.maximize and val > self.best_value:
                    self.best_value = val
                    self.best_node = node
                elif not self.maximize and val < self.best_value:
                    self.best_value = val
                    self.best_node = node
                continue

            # --- Podziału (branching) ---
            for child in node.branch():
                if self.maximize:
                    if child.bound() > self.best_value:
                        heapq.heappush(heap, child)
                else:
                    if child.bound() < self.best_value:
                        heapq.heappush(heap, child)

        return self.best_node



@dataclass
class Item:
    weight: float
    value: float


@dataclass
class KnapsackNode(Node):
    """Węzeł dla problemu plecakowego 0/1."""

    items: List[Item]           # wszystkie przedmioty
    capacity: float             # pojemność plecaka
    index: int                  # indeks następnego rozważanego przedmiotu
    current_weight: float       # aktualny ciężar w plecaku
    current_value: float        # aktualna wartość w plecaku
    taken: List[int] = field(default_factory=list)  # indeksy wziętych przedmiotów

    # ---- Interfejs Node ----

    def is_complete(self) -> bool:
        return self.index >= len(self.items)

    def value(self) -> float:
        return self.current_value

    def bound(self) -> float:
        """
        Ograniczenie górne metodą ułamkowego plecaka (relaksacja LP).
        Przedmioty posortowane malejąco wg value/weight.
        """
        if self.current_weight > self.capacity:
            return 0.0

        bound_value = self.current_value
        remaining = self.capacity - self.current_weight

        # Bierzemy przedmioty frakcyjnie od najlepszego stosunku v/w
        sorted_items = sorted(
            self.items[self.index:],
            key=lambda it: it.value / it.weight if it.weight > 0 else float("inf"),
            reverse=True,
        )

        for it in sorted_items:
            if remaining <= 0:
                break
            take = min(it.weight, remaining)
            bound_value += (take / it.weight) * it.value
            remaining -= take

        return bound_value

    def branch(self) -> List["KnapsackNode"]:
        if self.index >= len(self.items):
            return []

        item = self.items[self.index]
        children = []

        # Gałąź 1: bierzemy przedmiot
        if self.current_weight + item.weight <= self.capacity:
            children.append(KnapsackNode(
                items=self.items,
                capacity=self.capacity,
                index=self.index + 1,
                current_weight=self.current_weight + item.weight,
                current_value=self.current_value + item.value,
                taken=self.taken + [self.index],
            ))

        # Gałąź 2: pomijamy przedmiot
        children.append(KnapsackNode(
            items=self.items,
            capacity=self.capacity,
            index=self.index + 1,
            current_weight=self.current_weight,
            current_value=self.current_value,
            taken=self.taken[:],
        ))

        return children


def knapsack_example() -> None:
    items = [
        Item(weight=2, value=6),
        Item(weight=2, value=10),
        Item(weight=2, value=12),
        Item(weight=1, value=4),
        Item(weight=5, value=14),
    ]
    capacity = 7.0

    root = KnapsackNode(
        items=items,
        capacity=capacity,
        index=0,
        current_weight=0.0,
        current_value=0.0,
    )

    solver = BranchAndBound(maximize=True)
    best = solver.solve(root)

    print("=== Problem Plecakowy 0/1 ===")
    print(f"Pojemność plecaka : {capacity}")
    for i, it in enumerate(items):
        print(f"  Przedmiot {i}: waga={it.weight}, wartość={it.value}")
    print()
    if best:
        print(f"Optymalna wartość  : {best.value()}")
        print(f"Wzięte przedmioty  : {best.taken}")
        total_w = sum(items[i].weight for i in best.taken)
        print(f"Łączna waga        : {total_w}")
    print(f"Przeszukane węzły  : {solver.nodes_explored}")


if __name__ == "__main__":
    knapsack_example()

    # --------------------------------------------------------
    # WSTAW TUTAJ WŁASNY PROBLEM
    # --------------------------------------------------------
    # 1. Zdefiniuj klasę dziedziczącą po Node (np. MyProblemNode)
    #    i zaimplementuj: is_complete, value, bound, branch
    #
    # 2. Utwórz węzeł-korzeń:
    #    root = MyProblemNode(...)
    #
    # 3. Uruchom solver:
    #    solver = BranchAndBound(maximize=True)   # lub False
    #    best   = solver.solve(root)
    #
    # 4. Odczytaj wynik:
    #    print(best.value())
    # --------------------------------------------------------
