
import sys
from typing import List
import numpy as np
# CPLEX_PATH = "C:\Program Files\IBM\ILOG\CPLEX_Studio201\cplex\python\\3.7\\x64_win64"
# sys.path.append(CPLEX_PATH)

# import setup
from docplex.mp.model import Model
from docplex.util.environment import get_environment


class ParkAllocModel(Model):

    def __init__(self, source: List, target: List, cap={}, demand={}, costs={}):
        super(ParkAllocModel, self).__init__()
        if not isinstance(cap, dict):
            raise TypeError("capacities must be dict, not %s" % (
                cap.__class__.__name__,
            ))
        if not isinstance(demand, dict):
            raise TypeError("demand must be dict, not %s" % (
                demand.__class__.__name__,
            ))
        if not isinstance(costs, dict):
            raise TypeError("costs must be dict, not %s" % (
                costs.__class__.__name__,
            ))
        self._source = source
        self._target = target
        self._capacities = cap.copy()  # default arguments are mutable, use a copy to prevent unexpected behaviour
        self._demand = demand.copy()   # or use: attrib=None; attrib = attrib or {}
        self._costs = costs.copy()
        self._x = {(i, j): self.integer_var(name='x_{0}_{1}'.format(i, j))
                   for i in self._source for j in self._target}
        for i in self._source:
            self.add_constraint(self.sum(self._x[(i, j)] for j in self._target) == self._capacities[i])
        for j in self._target:
            self.add_constraint(self.sum(self._x[(i, j)] for i in self._source) <= self._demand[j])

    def solve_model(self, save=False, genetic_alg_init=False):
        # self.print_information()
        self.minimize(self.sum(self._x[(i, j)] * self._costs.get((i, j), np.inf)
                               for i in self._source for j in self._target))
        # self.parameters.lpmethod = 4
        if self.solve(log_output=False) is None:
            raise ValueError(f'Model is infeasible. Solver returned {self.solve()}')
        self.float_precision = 3
        self.parameters.mip.display.set(0)
        # self.print_solution()
        if genetic_alg_init:
            pop_ini = np.zeros((len(self._source), len(self._target)), dtype=int)
            for idx, var in enumerate(self.solution.iter_variables()):
                pop_ini[idx][int(var.to_string().split("_")[2])] = 1
                # print(idx, int(var.to_string().split("_")[2]))
            return pop_ini
            # print(idx, var.to_string().split("_")[2], self.solution[var], self.solution.get_var_value(var))

        if save:
            with get_environment().get_output_stream("park_alloc_solution.json") as fp:
                self.solution.export(fp, "json")
        # self.solve().display()
        print(self.solution.get_objective_value())
        return self.solution.get_objective_value()
