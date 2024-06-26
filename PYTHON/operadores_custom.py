# operadores_custom.py

from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.core.mutation import Mutation
from constantes import *
import numpy as np


class CustomIntegerRandomSampling(IntegerRandomSampling):
    def __init__(self, problem):
        super().__init__()
        self.problem = problem

    def _do(self, problem, n_samples, **kwargs):

        matriz = np.full((n_samples, problem.n_var), np.nan)    # Inicializacion matriz (NUM_POB * NUM_GEN)

        for i in range(n_samples):            
            for dia in range(NUM_DIAS):
                indice_dia = dia * NUM_ALIMENTOS_DIARIO     # Posicion inicial del dia (0, 11, 22, ...)

                for comida in COMIDAS:
                    num_alimentos = comida["num_alimentos"]

                    for indice_alimento in range(num_alimentos):
                        
                        match comida["nombre"]:

                            case "Tentempie" | "Merienda":
                                matriz[i, indice_dia] = np.random.choice(self.problem.snacks)

                            case "Desayuno":
                                if indice_alimento == 2:
                                    matriz[i, indice_dia] = np.random.choice(self.problem.bebida_desayuno)
                                else:
                                    matriz[i, indice_dia] = np.random.choice(self.problem.desayuno)

                            case _:
                                if indice_alimento == 2:
                                    matriz[i, indice_dia] = np.random.choice(self.problem.bebidas)
                                else:
                                    matriz[i, indice_dia] = np.random.choice(self.problem.almuerzo_cena)

                        indice_dia += 1
        
        return matriz



class CustomMutation(Mutation):
    def __init__(self, problem, prob_mutation):
        super().__init__()
        self.problem = problem
        self.prob_mutation = prob_mutation

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            for dia in range(NUM_DIAS):
                indice_dia = dia * NUM_ALIMENTOS_DIARIO

                for comida in COMIDAS:
                    num_alimentos = comida["num_alimentos"]

                    for indice_alimento in range(num_alimentos):
                        if np.random.rand() < self.prob_mutation:

                            match comida["nombre"]:

                                case "Tentempie" | "Merienda":
                                    X[i, indice_dia] = np.random.choice(problem.snacks)

                                case "Desayuno":
                                    if indice_alimento == 2:
                                        X[i, indice_dia] = np.random.choice(problem.bebida_desayuno)

                                    else:
                                        X[i, indice_dia] = np.random.choice(problem.desayuno)

                                case _:
                                    if indice_alimento == 2:
                                        X[i, indice_dia] = np.random.choice(problem.bebidas)
                                        
                                    else:
                                        X[i, indice_dia] = np.random.choice(problem.almuerzo_cena)

                        indice_dia += 1

        return X