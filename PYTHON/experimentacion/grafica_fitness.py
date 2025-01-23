# grafica_fitness.py

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PYTHON.utilidades import database, constantes
from PYTHON.experimentacion.ejecutar_guardar_resultados import cargar_sujetos

from PYTHON.algoritmos.spea2 import ag_spea2_estatica, ag_spea2_separatista


def ejecutar_algoritmo(metodo, conexion_bd, sujeto, seed):
    """Ejecuta el algoritmo segun el metodo elegido."""

    if metodo == "penalizacion_estatica":
        return ag_spea2_estatica.ejecutar_algoritmo_genetico(
            comida_basedatos=conexion_bd,
            objetivo_calorico=sujeto['calorias'],
            edad=sujeto['edad'],
            grupos_alergia=sujeto['alergias'],
            grupos_gusta=sujeto['gustos'],
            grupos_no_gusta=sujeto['disgustos'],
            seed=seed
        )
    elif metodo == "separatista":
        return ag_spea2_separatista.ejecutar_algoritmo_genetico(
            comida_basedatos=conexion_bd,
            objetivo_calorico=sujeto['calorias'],
            edad=sujeto['edad'],
            grupos_alergia=sujeto['alergias'],
            grupos_gusta=sujeto['gustos'],
            grupos_no_gusta=sujeto['disgustos'],
            seed=seed
        )
    else:
        print("Error")

def calcular_fitness_por_generacion(resultado, metodo):
    """Obtiene los valores de fitness por generacion."""

    fitness_por_generacion = {}

    for generacion_idx, poblacion_actual in enumerate(resultado.history):
        if generacion_idx not in fitness_por_generacion:
            fitness_por_generacion[generacion_idx] = []

        if metodo == "penalizacion_estatica":
            valores_fitness = poblacion_actual.pop.get("raw")  
        else:
            valores_fitness = poblacion_actual.pop.get("F") 

        for fitness_individual in valores_fitness:
            fitness_por_generacion[generacion_idx].append(fitness_individual)

    return fitness_por_generacion


def calcular_media_por_generacion(fitness_por_generacion):
    """Calcula el promedio de cada objetivo por generacion."""

    fitness_calorias_gen = []
    fitness_macros_gen = []
    fitness_prefer_gen = []

    for gen_idx in sorted(fitness_por_generacion.keys()):
        soluciones_generacion = fitness_por_generacion[gen_idx]

        calorias_list = []
        macros_list = []
        prefer_list = []

        for (calorias, macronutrientes, preferencias) in soluciones_generacion:
            calorias_list.append(calorias)
            macros_list.append(macronutrientes)
            prefer_list.append(preferencias)

        fitness_calorias_gen.append(np.mean(calorias_list))
        fitness_macros_gen.append(np.mean(macros_list))
        fitness_prefer_gen.append(np.mean(prefer_list))

    return fitness_calorias_gen, fitness_macros_gen, fitness_prefer_gen

def generar_graficas(metodo="penalizacion_estatica"):
    """Genera graficas de evolucion de fitness."""

    conexion_bd = database.conexion_comida_basedatos()
    sujetos = cargar_sujetos()

    lista_generaciones_sujeto = []

    for sujeto in sujetos:
        soluciones_acumuladas = {}

        for seed in constantes.SEEDS:
            resultado = ejecutar_algoritmo(metodo, conexion_bd, sujeto, seed)
            sol_por_gen = calcular_fitness_por_generacion(resultado, metodo)

            for gen_idx, soluciones_objetivo in sol_por_gen.items():
                if gen_idx not in soluciones_acumuladas:
                    soluciones_acumuladas[gen_idx] = []
                soluciones_acumuladas[gen_idx].extend(soluciones_objetivo)

        fitness_calorias, fitness_macros, fitness_prefer = calcular_media_por_generacion(soluciones_acumuladas)
        lista_generaciones_sujeto.append((fitness_calorias, fitness_macros, fitness_prefer))

    objetivos = ["Calorías", "Macronutrientes", "Preferencias"]

    for obj_idx, obj_nombre in enumerate(objetivos):

        plt.figure()

        for sujeto_idx, (fitness_calorias, fitness_macros, fitness_prefer) in enumerate(lista_generaciones_sujeto):
            if obj_idx == 0:
                valores_fitness = fitness_calorias
            elif obj_idx == 1:
                valores_fitness = fitness_macros
            else:
                valores_fitness = fitness_prefer

            generaciones = range(1, len(valores_fitness) + 1)
            plt.plot(generaciones, valores_fitness, label=f"Sujeto {sujeto_idx + 1}")

        plt.title(f"Evolución del Fitness - {obj_nombre} - {metodo}")
        plt.xlabel("Generaciones")
        plt.ylabel(f"Fitness Promedio ({obj_nombre})")
        plt.legend()
        plt.grid(True)

        nombre_archivo = f"fitness_{metodo}_{obj_nombre.lower()}.png"
        plt.savefig(nombre_archivo)
        plt.show()

        print("Grafica guardada:", nombre_archivo)

if __name__ == "__main__":
    """Ejecucion principal del script."""

    metodo = "penalizacion_estatica"  
    if len(sys.argv) > 1:
        metodo = sys.argv[1]
    generar_graficas(metodo)
