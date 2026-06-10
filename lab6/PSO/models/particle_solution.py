from dataclasses import dataclass


@dataclass
class Particle:
    position: list[float]
    velocity: list[float]
    local_memory: list[float]
    