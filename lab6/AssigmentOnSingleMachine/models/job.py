from dataclasses import dataclass

@dataclass
class Job:
    index: int
    duration: int
    weight: int
    deadline: int | None = None