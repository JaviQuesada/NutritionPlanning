#algoritmo_genetico

# Importamos las librerías necesarias
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.optimize import minimize
import numpy as np
from database import conexion_comida_basedatos
from solucion_traducida import traducir_solucion, print_solucion


comida_basedatos = conexion_comida_basedatos()

# Clase del problema de optimización
class PlanningComida(ElementwiseProblem):
    
        def __init__(self, comida_basedatos):

            super().__init__(n_var=42, n_obj=1, n_constr=1, xl=0, xu=len(comida_basedatos)-1)  
            self.comida_basedatos = comida_basedatos


        def _evaluate(self, x, out, *args, **kwargs):

            infracciones_semanales = 0
            infracciones_diarias = []
            total_calorias_semanales = 0

            for dia in range(7):
                calorias_diarias = 0
                
                for comida in range(3):

                    for indice_alimento in range(2):
                        alimento = self.comida_basedatos[int(x[dia * 6 + comida * 2 + indice_alimento])]
                        calorias_diarias += alimento["calorias"]

                total_calorias_semanales += calorias_diarias

                # Añadir restricciones si las calorías diarias no están dentro del rango permitido
                if calorias_diarias < 1800 or calorias_diarias > 2200:
                    infracciones_semanales += 1
                    infracciones_diarias.append(max(1800 - calorias_diarias, calorias_diarias - 2200))
                else:
                    infracciones_diarias.append(0)

            # Establecer el objetivo de minimizar las restricciones
            out["F"] = infracciones_semanales
            out["G"] = np.array([sum(infracciones_diarias)])


# Algoritmo genético
problema = PlanningComida(comida_basedatos)

algoritmo = GA(
    pop_size=100,  # Tamaño de la población
    sampling=FloatRandomSampling(), # Solucion inicial aleatoria
    crossover=SBX(prob=0.9, eta=15),  # Cruzamiento
    mutation=PolynomialMutation(prob=1/42, eta=20),  # Mutación
    eliminate_duplicates=True,
    seed=8947   # Semilla
)

resultado = minimize(
    problema,
    algoritmo,
    ('n_gen', 100),  # Número de generaciones
    verbose=True
)

# Procesar y mostrar la solución si existe
if resultado.X is not None:
    translated_solution = traducir_solucion(resultado.X, comida_basedatos)
    print_solucion(translated_solution)
    print("Valor del objetivo (Suma de desviaciones diarias respecto a 2000 calorías):", resultado.F)
else:
    print("No se encontró una solución")













