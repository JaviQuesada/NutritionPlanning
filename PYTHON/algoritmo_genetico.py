#algoritmo_genetico

# Importamos librerías
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
    
        def __init__(self, comida_basedatos, objetivo_calorico):

            super().__init__(n_var=42, n_obj=1, n_constr=1, xl=0, xu=len(comida_basedatos)-1)  
            self.comida_basedatos = comida_basedatos
            self.objetivo_calorico = objetivo_calorico


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
                if calorias_diarias < (self.objetivo_calorico * 0.9) or calorias_diarias > (self.objetivo_calorico * 1.1):
                    infracciones_semanales += 1
                    infracciones_diarias.append(max(1800 - calorias_diarias, calorias_diarias - 2200))
                else:
                    infracciones_diarias.append(0)

            # Establecer el objetivo de minimizar las restricciones
            out["F"] = infracciones_semanales
            out["G"] = np.array([sum(infracciones_diarias)])



def ejecutar_algoritmo_generico(comida_basedatos, objetivo_calorico):

    problema = PlanningComida(comida_basedatos, objetivo_calorico)

    algoritmo = GA(
        pop_size=100,  # Tamaño de la población
        sampling=FloatRandomSampling(), # Solucion inicial aleatoria
        crossover=SBX(prob=0.9, eta=15),  # Cruzamiento
        mutation=PolynomialMutation(prob=1/42, eta=20),  # Mutación
        eliminate_duplicates=True,
        seed=42   # Semilla
    )

    resultado = minimize(
        problema,
        algoritmo,
        ('n_gen', 200),  # Número de generaciones
        verbose=True
    )

    # Mostrar la solución
    if resultado.X is not None:
        translated_solution = traducir_solucion(resultado.X, comida_basedatos)
        print_solucion(translated_solution)
        print("Días que no cumple objetivos:", int(resultado.F))
    else:
        print("No se encontró una solución")













