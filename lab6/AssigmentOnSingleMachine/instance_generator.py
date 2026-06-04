from models.job import Job
from models.instance import Instance
from random_number_generator import RandomNumberGenerator
import math

def generate_instance(number_of_jobs: int, seed: int):

    duration_sum = 0
    jobs_list = []
    random_generator = RandomNumberGenerator(seed)

    for i in range(number_of_jobs):
        weight = random_generator.nextInt(1,10)
        duration = random_generator.nextInt(1,100)
        job = Job(i, duration, weight)
        jobs_list.append(job)
        duration_sum += duration


    for job in jobs_list:
        deadline = random_generator.nextInt(math.floor(duration_sum/4),math.floor(duration_sum/2))
        job.deadline = deadline

    return Instance(jobs_list)