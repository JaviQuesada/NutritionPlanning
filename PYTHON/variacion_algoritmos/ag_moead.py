#algoritmo_genetico_moead

# Importamos librerias
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions

from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.pntx import SinglePointCrossover
from pymoo.optimize import minimize

from operadores_custom import CustomIntegerRandomSampling, CustomMutation
from funciones_auxiliares import calculo_macronutrientes, filtrar_comida
from database import conexion_comida_basedatos
from solucion_traducida import traducir_solucion, mostrar_menu
from constantes import *

import numpy as np

from pymoo.config import Config
Config.warnings['not_compiled'] = False

comida_basedatos = conexion_comida_basedatos()


def objetivo_calorias(calorias_diarias, objetivo_calorico):

    desviacion_objetivo_calorias = abs(objetivo_calorico - calorias_diarias)

    return desviacion_objetivo_calorias

def restriccion_calorias(calorias_diarias, objetivo_calorico):

    limite_inferior = objetivo_calorico * 0.9
    limite_superior = objetivo_calorico * 1.1

    if calorias_diarias < limite_inferior or calorias_diarias > limite_superior:
        penalizacion_calorias = abs(objetivo_calorico - calorias_diarias) * PENALIZACION_CALORIAS
    else:
        penalizacion_calorias = 0

    return penalizacion_calorias


def objetivo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias):

    porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias)

    desviacion_objetivo_proteinas = abs(porcentaje_proteinas - OBJETIVO_PROTEINAS)
    desviacion_objetivo_carbohidratos = abs(porcentaje_carbohidratos - OBJETIVO_CARBOHIDRATOS)
    desviacion_objetivo_grasas = abs(porcentaje_grasas - OBJETIVO_GRASAS)

    desviacion_macronutrientes = desviacion_objetivo_proteinas + desviacion_objetivo_carbohidratos + desviacion_objetivo_grasas

    return desviacion_macronutrientes

def restriccion_macronutrientes (calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias):

    porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias)

    penalizacion_macronutrientes = 0

    if porcentaje_proteinas < LIMITE_PROTEINAS[0] or porcentaje_proteinas > LIMITE_PROTEINAS[1]:
        penalizacion_macronutrientes += abs(porcentaje_proteinas - OBJETIVO_PROTEINAS) * PENALIZACION_MACRONUTRIENTES

    if porcentaje_carbohidratos < LIMITE_CARBOHIDRATOS[0] or porcentaje_carbohidratos > LIMITE_CARBOHIDRATOS[1]:
        penalizacion_macronutrientes += abs(porcentaje_carbohidratos - OBJETIVO_CARBOHIDRATOS) * PENALIZACION_MACRONUTRIENTES

    if porcentaje_grasas < LIMITE_GRASAS[0] or porcentaje_grasas > LIMITE_GRASAS[1]:
        penalizacion_macronutrientes += abs(porcentaje_grasas - OBJETIVO_GRASAS) * PENALIZACION_MACRONUTRIENTES

    return penalizacion_macronutrientes


def objetivo_preferencia_grupo(alimento, grupos_gusta, grupos_no_gusta):

    penalizacion = 0

    if alimento["grupo"] in grupos_gusta:
        penalizacion = -PENALIZACION_PREFERENCIA
    if alimento["grupo"] in grupos_no_gusta:
        penalizacion = PENALIZACION_PREFERENCIA

    return penalizacion


def restriccion_alergia(alimento, grupos_alergia):

    if alimento["grupo"] in grupos_alergia:
        return PENALIZACION_ALERGIA
    else:
        return 0



# Clase del problema de optimizacion
class PlanningComida(ElementwiseProblem):
    
        def __init__(self, comida_basedatos, objetivo_calorias, grupos_alergia, grupos_gusta, grupos_no_gusta):

            super().__init__(n_var=NUM_GENES, n_obj=3, n_constr=0, xl=0, xu=len(comida_basedatos)-1)  
            self.comida_basedatos = comida_basedatos
            self.objetivo_calorias = objetivo_calorias
            self.grupos_alergia = grupos_alergia
            self.grupos_gusta = grupos_gusta
            self.grupos_no_gusta = grupos_no_gusta
            
            self.almuerzo_cena = filtrar_comida(comida_basedatos, "almuerzo_cena")
            self.bebidas = filtrar_comida(comida_basedatos, "bebidas")
            self.desayuno = filtrar_comida(comida_basedatos, "desayuno")
            self.bebida_desayuno = filtrar_comida(comida_basedatos, "bebida_desayuno") 
            self.snacks = filtrar_comida(comida_basedatos, "snacks")


        def _evaluate(self, x, out, *args, **kwargs):

            total_desviaciones_calorias = 0
            total_penalizaciones_calorias = 0

            total_desviaciones_macronutrientes = 0
            total_penalizaciones_macronutrientes = 0

            total_penalizaciones_preferencia = 0
            total_penalizaciones_alergia = 0


            for dia in range(NUM_DIAS):
                calorias_diarias = 0
                calorias_por_comida = []

                proteinas_diarias = 0
                carbohidratos_diarias = 0
                grasas_diarias = 0

                suma_num_alimentos = 0
                
                for indice_comida, comida in enumerate(COMIDAS):

                    num_alimentos = comida["num_alimentos"]

                    calorias_comida = 0

                    for indice_alimento in range(num_alimentos):

                        alimento = self.comida_basedatos[int(x[(dia * NUM_ALIMENTOS_DIARIO) + suma_num_alimentos + indice_alimento])]

                        calorias_diarias += alimento["calorias"]
                        calorias_comida += calorias_diarias

                        proteinas_diarias += alimento["proteinas"]
                        carbohidratos_diarias += alimento["carbohidratos"]
                        grasas_diarias += alimento["grasas"]

                        total_penalizaciones_preferencia += objetivo_preferencia_grupo(alimento, self.grupos_gusta, self.grupos_no_gusta)
                        total_penalizaciones_alergia += restriccion_alergia(alimento, self.grupos_alergia)


                    suma_num_alimentos = suma_num_alimentos + num_alimentos
                    calorias_por_comida.append(calorias_comida)


                desviacion_objetivo_calorias = objetivo_calorias(calorias_diarias, self.objetivo_calorias)
                total_desviaciones_calorias += desviacion_objetivo_calorias

                penalizacion_objetivo_calorias = restriccion_calorias(calorias_diarias, self.objetivo_calorias)
                total_penalizaciones_calorias += penalizacion_objetivo_calorias


                desviacion_objetivo_macronutrientes = objetivo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias)
                total_desviaciones_macronutrientes += desviacion_objetivo_macronutrientes

                penalizacion_objetivo_macronutriente = restriccion_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias)
                total_penalizaciones_macronutrientes += penalizacion_objetivo_macronutriente


            total_penalizacion = total_penalizaciones_alergia + total_penalizaciones_calorias + total_penalizaciones_macronutrientes

            fitness_objetivo_calorias = total_desviaciones_calorias + total_penalizacion
            fitness_objetivo_macronutrientes = total_desviaciones_macronutrientes + total_penalizacion
            fitness_objetivo_preferencia = total_penalizaciones_preferencia + total_penalizacion


            # Establece el objetivo de minimizar las restricciones
            out["F"] = np.array([fitness_objetivo_calorias, fitness_objetivo_macronutrientes, fitness_objetivo_preferencia])
            


def ejecutar_algoritmo_genetico(comida_basedatos, objetivo_calorico, grupos_alergia, grupos_gusta, grupos_no_gusta):

    problema = PlanningComida(comida_basedatos, objetivo_calorico, grupos_alergia, grupos_gusta, grupos_no_gusta)

    # Definir direcciones de referencia para MOEA/D
    ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)

    algoritmo = MOEAD(
        ref_dirs=ref_dirs,
        n_neighbors=15,
        prob_neighbor_mating=0.7,
        sampling=CustomIntegerRandomSampling(problema),
        crossover=SinglePointCrossover(prob=1),
        mutation=CustomMutation(problema, prob_mutation=1/77)
    )

    resultado = minimize(
        problema,
        algoritmo,
        ('n_gen', 100),  # Número de generaciones
        verbose=True,
        save_history=True
    )

    # Obtener la mejor solucion encontrada
    mejor_solucion = resultado.pop.get("X")[np.argmin(resultado.pop.get("F")[:, 0])]
    
    # Traducir la solucion
    menu = traducir_solucion(mejor_solucion, comida_basedatos)
    
    # Mostrar el menu
    mostrar_menu(menu)

    
    











