#algoritmo_genetico

# Importamos librerías
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.pntx import SinglePointCrossover
from pymoo.operators.mutation.rm import ChoiceRandomMutation
from pymoo.optimize import minimize
import numpy as np
from database import conexion_comida_basedatos
from solucion_traducida import traducir_solucion, print_solucion


comida_basedatos = conexion_comida_basedatos()

class Variable:
    def __init__(self, max_val):
        self.max_val = max_val

    def sample(self, num_samples):
        return np.random.randint(0, self.max_val, size=num_samples)

# Clase del problema de optimización
class PlanningComida(ElementwiseProblem):
    
        def __init__(self, comida_basedatos, objetivo_calorico):

            super().__init__(n_var=42, n_obj=1, n_constr=1, xl=0, xu=len(comida_basedatos)-1)  
            self.comida_basedatos = comida_basedatos
            self.objetivo_calorico = objetivo_calorico
            self.vars = {i: Variable(len(comida_basedatos)) for i in range(42)}


        def _evaluate(self, x, out, *args, **kwargs):

            penalizacion_fuera = 0
            total_diferencias = 0
            infraccion = 0

            for dia in range(7):
                calorias_diarias = 0
                
                for comida in range(3):

                    for indice_alimento in range(2):
                        alimento = self.comida_basedatos[int(x[dia * 6 + comida * 2 + indice_alimento])]
                        calorias_diarias += alimento["calorias"]

                limite_inferior = self.objetivo_calorico * 0.9
                limite_superior = self.objetivo_calorico * 1.1

                diferencia_diaria = abs(self.objetivo_calorico - calorias_diarias)

                # Añade restricciones si las calorías diarias no están dentro del rango permitido
                if limite_inferior <= calorias_diarias <= limite_superior:  
                    total_diferencias += diferencia_diaria
                else:
                    penalizacion_fuera += diferencia_diaria * 10
                    infraccion += 1

            fitness_total = total_diferencias + penalizacion_fuera
            # Establece el objetivo de minimizar las restricciones
            out["F"] = np.array([fitness_total])
            out["G"] = np.array([infraccion])



def ejecutar_algoritmo_generico(comida_basedatos, objetivo_calorico):

    problema = PlanningComida(comida_basedatos, objetivo_calorico)

    algoritmo = GA(
        pop_size=100,  # Tamaño de la población
        sampling=FloatRandomSampling(), # Solucion inicial aleatoria
        crossover=SinglePointCrossover(prob=1),  # Cruzamiento
        mutation=ChoiceRandomMutation(prob=1/42),  # Mutación
        eliminate_duplicates=True,
        seed=42   # Semilla
    )

    resultado = minimize(
        problema,
        algoritmo,
        ('n_gen', 100),  # Número de generaciones
        verbose=True
    )
    
    # Mostrar la solución
    if resultado.X is not None:
        translated_solution = traducir_solucion(resultado.X, comida_basedatos)
        print_solucion(translated_solution)

        if resultado.G[0] == 0:
            print("La solución es óptima")
        else:
            print("Días que no cumple objetivos:", resultado.G[0])
    else:
        print("No se encontró una solución")
    

    
    











