#algoritmo_genetico

# Importamos librerías
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.pntx import SinglePointCrossover
from pymoo.optimize import minimize

from operadores_custom import CustomIntegerRandomSampling, CustomMutation
from funciones_auxiliares import calculo_macronutrientes
from database import conexion_comida_basedatos
from solucion_traducida import traducir_solucion, print_solucion
from constantes import *

import numpy as np

from pymoo.config import Config
Config.warnings['not_compiled'] = False

comida_basedatos = conexion_comida_basedatos()


def objetivo_calorias(calorias_diarias, objetivo_calorico):

    desviacion_objetivo_calorias = abs(objetivo_calorico - calorias_diarias)

    limite_inferior = objetivo_calorico * 0.9
    limite_superior = objetivo_calorico * 1.1

    if calorias_diarias < limite_inferior or calorias_diarias > limite_superior:
        penalizacion_calorias = desviacion_objetivo_calorias * PENALIZACION_CALORIAS
    else:
        penalizacion_calorias = 0

    return desviacion_objetivo_calorias + penalizacion_calorias


def objetivo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias):

    porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias)

    objetivo_proteinas = abs(porcentaje_proteinas - OBJETIVO_PROTEINAS)
    objetivo_carbohidratos = abs(porcentaje_carbohidratos - OBJETIVO_CARBOHIDRATOS)
    objetivo_grasas = abs(porcentaje_grasas - OBJETIVO_GRASAS)
    
    penalizacion_macronutrientes = 0

    if porcentaje_proteinas < LIMITE_PROTEINAS[0] or porcentaje_proteinas > LIMITE_PROTEINAS[1]:
        penalizacion_macronutrientes += objetivo_proteinas * PENALIZACION_MACRONUTRIENTES

    if objetivo_carbohidratos < LIMITE_CARBOHIDRATOS[0] or objetivo_carbohidratos > LIMITE_CARBOHIDRATOS[1]:
        penalizacion_macronutrientes += objetivo_carbohidratos * PENALIZACION_MACRONUTRIENTES

    if objetivo_grasas < LIMITE_GRASAS[0] or objetivo_grasas > LIMITE_GRASAS[1]:
        penalizacion_macronutrientes += objetivo_grasas * PENALIZACION_MACRONUTRIENTES

    desviacion_macronutrientes = objetivo_proteinas + objetivo_carbohidratos + objetivo_grasas + penalizacion_macronutrientes

    return desviacion_macronutrientes


def objetivo_preferencia_supergrupo(alimento, supergrupo_gusta, supergrupo_no_gusta):

    penalizacion = 0

    if alimento["supergrupo"] == supergrupo_gusta:
        penalizacion = -PENALIZACION_PREFERENCIA
    if alimento["supergrupo"] == supergrupo_no_gusta:
        penalizacion = PENALIZACION_PREFERENCIA

    return penalizacion


def restriccion_alergia(alimento, supergrupo_alergia):

    if alimento["supergrupo"] == supergrupo_alergia:
        return PENALIZACION_ALERGIA
    else:
        return 0


def restriccion_bebida(alimento, indice_alimento):
    if indice_alimento == 2 and alimento["supergrupo"] != Supergrupo.BEBIDAS.value:
        return PENALIZACION_BEBIDA
    else:
        return 0


# Clase del problema de optimización
class PlanningComida(ElementwiseProblem):
    
        def __init__(self, comida_basedatos, objetivo_calorias, supergrupo_alergia, supergrupo_gusta, supergrupo_no_gusta):

            super().__init__(n_var=NUM_GENES, n_obj=4, n_constr=0, xl=0, xu=len(comida_basedatos)-1)  
            self.comida_basedatos = comida_basedatos
            self.objetivo_calorias = objetivo_calorias
            self.supergrupo_gusta = supergrupo_gusta
            self.supergrupo_no_gusta = supergrupo_no_gusta
            self.supergrupo_alergia = supergrupo_alergia

            self.bebidas = [i for i, item in enumerate(comida_basedatos) if item["supergrupo"] == "P"]
            self.alimentos = [i for i, item in enumerate(comida_basedatos) if item["supergrupo"] != "P"]


        def _evaluate(self, x, out, *args, **kwargs):

            penalizacion_limite = 0
            total_desviaciones_calorico = 0
            total_desviaciones_macronutrientes = 0
            total_penalizaciones_preferencia = 0
            total_penalizaciones_alergia = 0


            for dia in range(NUM_DIAS):
                calorias_diarias = 0
                proteinas_diarias = 0
                carbohidratos_diarias = 0
                grasas_diarias = 0
                
                for comida in range(NUM_COMIDAS):

                    for indice_alimento in range(NUM_ALIMENTOS_POR_COMIDA):

                        alimento = self.comida_basedatos[int(x[dia * NUM_COMIDAS * NUM_ALIMENTOS_POR_COMIDA + comida * NUM_ALIMENTOS_POR_COMIDA + indice_alimento])]

                        calorias_diarias += alimento["calorias"]
                        proteinas_diarias += alimento["proteinas"]
                        carbohidratos_diarias += alimento["carbohidratos"]
                        grasas_diarias += alimento["grasas"]

                        penalizacion_limite += restriccion_bebida(alimento, indice_alimento)
                        total_penalizaciones_preferencia += objetivo_preferencia_supergrupo(alimento, self.supergrupo_gusta, self.supergrupo_no_gusta)
                        total_penalizaciones_alergia += restriccion_alergia(alimento, self.supergrupo_alergia)


                desviacion_objetivo_calorico = objetivo_calorias(calorias_diarias, self.objetivo_calorias)
                total_desviaciones_calorico += desviacion_objetivo_calorico

                desviacion_objetivo_macronutrientes = objetivo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias)
                total_desviaciones_macronutrientes += desviacion_objetivo_macronutrientes


            fitness_calorico = total_desviaciones_calorico + penalizacion_limite
            fitness_macronutriente = total_desviaciones_macronutrientes
            fitness_alergia = total_penalizaciones_alergia
            fitness_preferencia = total_penalizaciones_preferencia

            # Establece el objetivo de minimizar las restricciones
            out["F"] = np.array([fitness_calorico, fitness_macronutriente, fitness_alergia, fitness_preferencia])
            


def ejecutar_algoritmo_genetico(comida_basedatos, objetivo_calorico, supergrupo_gusta, supergrupo_no_gusta, supergrupo_alergia):

    problema = PlanningComida(comida_basedatos, objetivo_calorico, supergrupo_gusta, supergrupo_no_gusta, supergrupo_alergia)

    algoritmo = NSGA2(
        pop_size=100,  # Tamaño de la población
        sampling=CustomIntegerRandomSampling(problema), # Solucion inicial aleatoria
        crossover=SinglePointCrossover(prob=1),  # Cruzamiento
        mutation=CustomMutation(problema, prob_mutation=0.1),  # Mutación
        eliminate_duplicates=True,
        #seed=63   # Semilla
    )

    resultado = minimize(
        problema,
        algoritmo,
        ('n_gen', 100),  # Número de generaciones
        verbose=True,
        save_history=True
    )
    

    mejor_fitness = np.argmin(np.sum(resultado.F, axis=1))
    mejor_solucion = resultado.X[mejor_fitness]

    # Mostrar la solución
    if mejor_solucion is not None:
        menu = traducir_solucion(mejor_solucion, comida_basedatos)
        print_solucion(menu)

        for f in resultado.F[mejor_fitness]:
            print(f"Fitness de la solución: {f:.4f}")
    else:
        print("No se encontró una solución")
    
    
    











