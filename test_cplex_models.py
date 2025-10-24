#! C:\Users\chaim\AppData\Local\Programs\Python\Python37\python.exe
"""
Install Python 3.6 or 3.7 in order to use CPLEX otherwise it won't work
"""

import sys
import os
import time
from typing import List
import numpy as np
import random

from cplex_models import ParkAllocModel
from dataloader import DataLoader


def test_park_alloc_model() -> None:
    source = list(range(1, 4))
    target = list(range(4, 8))
    cap = {1: 1, 2: 1, 3: 1}
    demand = {4: 3, 5: 1, 6: 2, 7: 4}
    costs = {(1, 4): 3, (1, 5): 5, (1, 6): 6,
             (1, 7): 1, (2, 4): 1, (2, 5): 8,
             (2, 6): 2, (2, 7): 7, (3, 4): 4,
             (3, 5): 9, (3, 6): 10, (3, 7): 3}
    gap = ParkAllocModel(source, target, cap, demand, costs)
    # print(gap._x)
    # print(gap.source)
    # print(gap.target)

    gap.solve_model()


def update_costs(costs: dict, charging_cost: np.ndarray, n_cars: int, n_parking: int) -> dict:
    # charging_cost = np.random.randint(30, 960, (n_cars, ))
    # print("charging cosgt = ", charging_cost[:10])
    total_cost = dict()
    for i in range(n_cars):
        for j in range(n_parking):
            total_cost[(i, j)] = costs[(i, j)] + charging_cost[i]
    return total_cost 


def test_simulated_data(filename: str, n_cars, n_parking, COST_UPDATED: bool=True) -> float:
    data_loader = DataLoader(filename, n_cars, n_parking)
    src, trg, cap = data_loader.load_src_trg_cap()
    demand, costs = data_loader.load_demand_cost()
    if COST_UPDATED:
        cost_folder = "D:/workspace/dev/smart_parking/PAP/Charging_time"
        charging_cost = data_loader.load_charging_time(cost_folder)
        # print(charging_cost.shape)
        new_costs = update_costs(costs, charging_cost, n_cars, n_parking)
        gap = ParkAllocModel(src, trg, cap, demand, new_costs)
        return gap.solve_model()
    gap = ParkAllocModel(src, trg, cap, demand, costs)
    return gap.solve_model()


def compute_average_obj_func(folder_name: str, n_instances: int = 10) -> List[float]:
    """
    compute the the average obj func over the 10 instances
    :param n_instances: instances
    :param folder_name: absolute path to the folder containing instances
    :return: the average objective function of the ten instances
    """
    cars = [int(os.path.splitext(f)[0].split('_')[0]) // 100 for f in os.listdir(folder_name)]
    parking = [int(os.path.splitext(f)[0].split('_')[0]) % 100 for f in os.listdir(folder_name)]
    obj_func = 0
    avg_func = []
    for i, s in enumerate(os.listdir(folder_name)):
        data_loader = DataLoader(os.path.join(folder_name, s), cars[i], parking[i])
        src, trg, cap = data_loader.load_src_trg_cap()
        demand, costs = data_loader.load_demand_cost()
        gap = ParkAllocModel(src, trg, cap, demand, costs)
        obj_func += gap.solve_model(genetic_alg_init=False)
        if not (i+1) % n_instances:  # save the average value each n_instances
            avg_func.append(obj_func / n_instances)
            obj_func = 0
            # print("i= ".format(i))
    return avg_func


if __name__ == '__main__':
    # m = MyFirstModel(12, 20, 100, 0.2, 0.4, 490)
    # test_my_first_model(m)
    # test_park_alloc_model()

    data_file = sys.argv[1]
    test_simulated_data(data_file, 7000, 30)
    ############# Computing average cost function ########################
    #data_folder = sys.argv[1] #"D:\workspace\dev\smart_parking\PAP\Feasible\7000"
    #start = time.time()
    #print(compute_average_obj_func(data_folder))
    #end = time.time()
    #print("Computing the the average obj func took {0} seconds".format(end - start))
    ##############################################################