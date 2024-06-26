#algoritmo_genetico_reparacion

# Importamos librerias
from pymoo.algorithms.moo.nsga2 import NSGA2
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


def objetivo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias):

    porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias)

    desviacion_objetivo_proteinas = abs(porcentaje_proteinas - OBJETIVO_PROTEINAS)
    desviacion_objetivo_carbohidratos = abs(porcentaje_carbohidratos - OBJETIVO_CARBOHIDRATOS)
    desviacion_objetivo_grasas = abs(porcentaje_grasas - OBJETIVO_GRASAS)

    desviacion_macronutrientes = desviacion_objetivo_proteinas + desviacion_objetivo_carbohidratos + desviacion_objetivo_grasas

    return desviacion_macronutrientes


def objetivo_preferencia_grupo(alimento, grupo_gusta, grupo_no_gusta):

    penalizacion = 0

    if alimento["grupo"] in grupo_gusta:
        penalizacion = -PENALIZACION_PREFERENCIA
    if alimento["grupo"] in grupo_no_gusta:
        penalizacion = PENALIZACION_PREFERENCIA

    return penalizacion


def reparar_solucion(solucion, problema, objetivo_calorico, grupo_alergia, num_intentos):
    
    solucion_reparada = solucion.copy()

    for dia in range(NUM_DIAS):
        calorias_diarias = 0
        proteinas_diarias = 0
        carbohidratos_diarias = 0
        grasas_diarias = 0

        inicio_dia = dia * NUM_ALIMENTOS_DIARIO

        # Calcular las calorías y macronutrientes del día
        for i in range(inicio_dia, inicio_dia + NUM_ALIMENTOS_DIARIO):
            alimento = problema.comida_basedatos[int(solucion_reparada[i])]
            calorias_diarias += alimento["calorias"]
            proteinas_diarias += alimento["proteinas"]
            carbohidratos_diarias += alimento["carbohidratos"]
            grasas_diarias += alimento["grasas"]

        # Calcular porcentajes de macronutrientes
        porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(
            calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias
        )

        intentos = 0
        # Ajustar las calorías y macronutrientes si están fuera del rango permitido
        while intentos < num_intentos and (
            not (objetivo_calorico * 0.9 <= calorias_diarias <= objetivo_calorico * 1.1) or \
            not (LIMITE_PROTEINAS[0] <= porcentaje_proteinas <= LIMITE_PROTEINAS[1]) or \
            not (LIMITE_CARBOHIDRATOS[0] <= porcentaje_carbohidratos <= LIMITE_CARBOHIDRATOS[1]) or \
            not (LIMITE_GRASAS[0] <= porcentaje_grasas <= LIMITE_GRASAS[1])):

            idx = np.random.randint(inicio_dia, inicio_dia + NUM_ALIMENTOS_DIARIO)
            alimento_actual = problema.comida_basedatos[int(solucion_reparada[idx])]

            nuevo_alimento_idx = seleccionar_nuevo_alimento(problema, idx, inicio_dia)
            nuevo_alimento = problema.comida_basedatos[nuevo_alimento_idx]

            if nuevo_alimento["grupo"] in grupo_alergia:
                intentos += 1
                continue

            calorias_diarias += nuevo_alimento["calorias"] - alimento_actual["calorias"]
            proteinas_diarias += nuevo_alimento["proteinas"] - alimento_actual["proteinas"]
            carbohidratos_diarias += nuevo_alimento["carbohidratos"] - alimento_actual["carbohidratos"]
            grasas_diarias += nuevo_alimento["grasas"] - alimento_actual["grasas"]

            solucion_reparada[idx] = nuevo_alimento_idx

            # Recalcular porcentajes de macronutrientes
            porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(
                calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias
            )

    return solucion_reparada

def seleccionar_nuevo_alimento(problema, idx, inicio_dia):
    
    suma_num_alimentos = 0

    for comida in COMIDAS:
        num_alimentos = comida["num_alimentos"]

        for indice_alimento in range(num_alimentos):
            if (inicio_dia + suma_num_alimentos + indice_alimento) == idx:
                match comida["nombre"]:
                    case "Tentempie" | "Merienda":
                        return np.random.choice(problema.snacks)
                    case "Desayuno":
                        if indice_alimento == 2:
                            return np.random.choice(problema.bebida_desayuno)
                        else:
                            return np.random.choice(problema.desayuno)
                    case _:
                        if indice_alimento == 2:
                            return np.random.choice(problema.bebidas)
                        else:
                            return np.random.choice(problema.almuerzo_cena)
        suma_num_alimentos += num_alimentos

    return -1  # En caso de error


# Clase del problema de optimizacion
class PlanningComida(ElementwiseProblem):
    
    def __init__(self, comida_basedatos, objetivo_calorias, grupo_alergia, grupo_gusta, grupo_no_gusta):
        super().__init__(n_var=NUM_GENES, n_obj=3, n_constr=0, xl=0, xu=len(comida_basedatos)-1)
        self.comida_basedatos = comida_basedatos
        self.objetivo_calorias = objetivo_calorias
        self.grupo_gusta = grupo_gusta
        self.grupo_no_gusta = grupo_no_gusta
        self.grupo_alergia = grupo_alergia

        self.almuerzo_cena = filtrar_comida(comida_basedatos, "almuerzo_cena")
        self.bebidas = filtrar_comida(comida_basedatos, "bebidas")
        self.desayuno = filtrar_comida(comida_basedatos, "desayuno")
        self.bebida_desayuno = filtrar_comida(comida_basedatos, "bebida_desayuno")
        self.snacks = filtrar_comida(comida_basedatos, "snacks")

    def _evaluate(self, x, out, *args, **kwargs):

        x_reparada = reparar_solucion(x, self, self.objetivo_calorias, self.grupo_alergia, 100)
        
        total_desviaciones_calorias = 0
        total_desviaciones_macronutrientes = 0
        total_penalizaciones_preferencia = 0

        for dia in range(NUM_DIAS):
            calorias_diarias = 0
            proteinas_diarias = 0
            carbohidratos_diarias = 0
            grasas_diarias = 0

            suma_num_alimentos = 0
            
            for indice_comida, comida in enumerate(COMIDAS):
                num_alimentos = comida["num_alimentos"]

                for indice_alimento in range(num_alimentos):
                    idx = (dia * NUM_ALIMENTOS_DIARIO) + suma_num_alimentos + indice_alimento
                    alimento = self.comida_basedatos[int(x_reparada[idx])]
                    
                    calorias_diarias += alimento["calorias"]
                    proteinas_diarias += alimento["proteinas"]
                    carbohidratos_diarias += alimento["carbohidratos"]
                    grasas_diarias += alimento["grasas"]
                    
                    total_penalizaciones_preferencia += objetivo_preferencia_grupo(alimento, self.grupo_gusta, self.grupo_no_gusta)
                
                suma_num_alimentos += num_alimentos

            desviacion_objetivo_calorias = objetivo_calorias(calorias_diarias, self.objetivo_calorias)
            total_desviaciones_calorias += desviacion_objetivo_calorias

            desviacion_objetivo_macronutrientes = objetivo_macronutrientes(calorias_diarias, proteinas_diarias, carbohidratos_diarias, grasas_diarias)
            total_desviaciones_macronutrientes += desviacion_objetivo_macronutrientes

        fitness_objetivo_calorias = total_desviaciones_calorias
        fitness_objetivo_macronutrientes = total_desviaciones_macronutrientes
        fitness_objetivo_preferencia = total_penalizaciones_preferencia

        out["F"] = np.array([fitness_objetivo_calorias, fitness_objetivo_macronutrientes, fitness_objetivo_preferencia])

            


def ejecutar_algoritmo_genetico(comida_basedatos, objetivo_calorico, grupo_gusta, grupo_no_gusta, grupo_alergia):

    problema = PlanningComida(comida_basedatos, objetivo_calorico, grupo_gusta, grupo_no_gusta, grupo_alergia)

    algoritmo = NSGA2(
        pop_size=100,  # Tamaño de la poblacion
        sampling=CustomIntegerRandomSampling(problema),  # Inicializacion personalizada
        crossover=SinglePointCrossover(prob=1),  # Cruzamiento
        mutation=CustomMutation(problema, prob_mutation=1/77),  # Mutacion personalizada
        eliminate_duplicates=True,
        # seed=63   # Semilla
    )

    resultado = minimize(
        problema,
        algoritmo,
        ('n_gen', 100),  # Numero de generaciones
        verbose=True,
        save_history=True
    )
    
# Obtener la mejor solucion encontrada
    sum_F = np.sum(resultado.pop.get("F"), axis=1)

    mejor_solucion = resultado.pop.get("X")[np.argmin(sum_F)]
    
    # Traducir la solucion
    menu = traducir_solucion(mejor_solucion, comida_basedatos)
   
    # Mostrar el menu
    mostrar_menu(menu)