
import numpy as np
import os
import sys


class DataLoader:
    def __init__(self, filename: str, n_cars: int, n_parking: int, MODE='CPLEX'):
        self._filename = filename
        if not os.path.exists(self._filename):
            raise ValueError("File {0} does not exist !".format(self._filename))
        self._cars = n_cars
        self._parking = n_parking
        self._MODE = MODE

    def load_demand_cost(self):
        with open(self._filename, 'r') as f:
            raw_data = f.readlines()
        # assert(
        #    int(raw_data[0].strip().split()[0]) == self._cars and
        #    int(raw_data[0].strip().split()[1]) == self._parking
        # )
        parsed = [line.strip().split() for line in raw_data]
        t_prime = np.array(parsed[2:self._cars+2], dtype=int)
        t_second = np.array(parsed[self._cars+2:2*self._cars+2], dtype=int)
        costs = t_prime + t_second
        demand = np.array(parsed[2*self._cars+2], dtype=int)
        print(demand.shape)
        if self._MODE == 'CPLEX':
            assert demand.shape[0] == self._parking
            re_demand, re_costs = dict(), dict()
            for i in range(self._parking):
                re_demand[i] = demand[i]
            for i in range(self._cars):
                for j in range(self._parking):
                    re_costs[(i, j)] = costs[i, j]
            return re_demand, re_costs
        elif self._MODE == 'RANDOM':
            return demand, costs

    def load_src_trg_cap(self):
        cap = dict()
        for i in range(self._cars):
            cap[i] = 1
        return list(range(self._cars)), list(range(self._parking)), cap

    def load_charging_time(self, folder: str):
        # print(os.path.splitext(self._filename)[0])
        # print(os.path.splitext(os.path.basename(self._filename))[0].split("_")[1])
        return np.loadtxt(os.path.join(folder, "{0}_{1}.txt".format(self._cars,
                                                                    os.path.splitext(os.path.basename(self._filename))[0].split("_")[1])))


def export_charging_time(folder: str):
    if not os.path.exists(folder):
        os.mkdir(folder)
    n_cars = [1000, 3000, 5000, 7000, 9000]
    for i in n_cars:
        for j in range(1, 11):
            np.savetxt(os.path.join(folder, "{0}_{1}.txt".format(i, j)), np.random.randint(30, 240, (i, ), dtype=int))


if __name__ == '__main__':
    # data_file = sys.argv[1]  # /home/mbo/workspace/dev/pap_dataset/Feasible/1000/100010_1.txt
    ################# some test ########################
    # data_folder = sys.argv[2]
    # cars = [int(os.path.splitext(f)[0].split('_')[0]) // 100 for f in os.listdir(data_folder)]
    # parking = [int(os.path.splitext(f)[0].split('_')[0]) % 100 for f in os.listdir(data_folder)]
    ####################################################
    # data_loader = DataLoader(data_file, 1000, 10)
    # source, target, cap = data_loader.load_src_trg_cap()
    # demand, cost = data_loader.load_demand_cost()
    # print(len(demand.keys()))
    # print(len(cost.keys()))
    out_folder = "D:/workspace/dev/smart_parking/PAP/Charging_time"
    export_charging_time(out_folder)
