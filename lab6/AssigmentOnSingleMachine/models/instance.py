from dataclasses import dataclass
from .job import Job

@dataclass
class Instance:
    jobs: list[Job]
