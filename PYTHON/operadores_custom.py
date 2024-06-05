# operadores_custom.py

from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.core.mutation import Mutation
import numpy as np

class CustomIntegerRandomSampling(IntegerRandomSampling):
    def __init__(self, problem):
        super().__init__()
        self.problem = problem

    def _do(self, problem, n_samples, **kwargs):
        samples = np.full((n_samples, problem.n_var), np.nan)
        for i in range(n_samples):
            for j in range(problem.n_var):
                if j % 3 == 2:
                    samples[i, j] = np.random.choice(problem.bebidas)
                else:
                    samples[i, j] = np.random.choice(problem.alimentos)
        return samples


class CustomMutation(Mutation):
    def __init__(self, problem, prob_mutation=0.1):
        super().__init__()
        self.problem = problem
        self.prob_mutation = prob_mutation

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            for j in range(problem.n_var):
                if np.random.rand() < self.prob_mutation:
                    if j % 3 == 2:
                        X[i, j] = np.random.choice(self.problem.bebidas)
                    else:
                        X[i, j] = np.random.choice(self.problem.alimentos)
        return X