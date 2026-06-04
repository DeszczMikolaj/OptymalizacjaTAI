from dataclasses import dataclass
from job import Job

@dataclass
class Solution:
    order: list[Job]
    objective_value: int