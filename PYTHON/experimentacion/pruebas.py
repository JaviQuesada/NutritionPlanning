import json
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from PYTHON.utilidades import database, constantes
from PYTHON.algoritmos.variacion_algoritmos import ag_moead

def cargar_sujetos():
    """Devuelve los datos de los sujetos de prueba."""

    return [
        {'calorias': 2877.19, 'edad': 17, 'alergias': ['S', 'SE', 'SEA', 'SEC', 'SN', 'SNA', 'SNC'], 'gustos': ['AC', 'AD', 'MCA'], 'disgustos': ['J', 'JA', 'JC', 'JK', 'JM', 'JR', 'BR']},
        {'calorias': 2567.85, 'edad': 30, 'alergias': ['A', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AI', 'AK', 'AM', 'AN', 'AO', 'AP', 'AS', 'AT'], 'gustos': ['BAE', 'FC', 'FE'], 'disgustos': ['C', 'CA', 'CD', 'CDE', 'CDH']},
        {'calorias': 3102.84, 'edad': 40, 'alergias': ['PAC', 'PCA', 'SNC'], 'gustos': ['MAC', 'DAP', 'SEA'], 'disgustos': ['BH', 'BJS', 'MIG']},
        {'calorias': 1710.50, 'edad': 55, 'alergias': ['F', 'FA', 'FC', 'FE'], 'gustos': ['AF', 'BNH'], 'disgustos': ['MB', 'QA', 'QC']},
        {'calorias': 1401.30, 'edad': 72, 'alergias': ['BA', 'BAB', 'BAE', 'BAH', 'BAK', 'BAR', 'BH'], 'gustos': ['AM', 'JC'], 'disgustos': ['MG', 'MR', 'PAC']}
    ]


def calcular_datos_dia(solucion, conexion_bd, dia):
    """Calcula y devuelve las calorias y macronutrientes de una solucion especifica para un dia determinado."""

    calorias_dia, proteinas_dia, carbohidratos_dia, grasas_dia = 0, 0, 0, 0
    suma_alimentos = 0

    for comida in constantes.COMIDAS:
        for _ in range(comida["num_alimentos"]):
            idx = int(solucion[dia * constantes.NUM_ALIMENTOS_DIARIO + suma_alimentos])
            alimento = conexion_bd[idx]
            calorias_dia += alimento["calorias"]
            proteinas_dia += alimento["proteinas"]
            carbohidratos_dia += alimento["carbohidratos"]
            grasas_dia += alimento["grasas"]
            suma_alimentos += 1

    return calorias_dia, proteinas_dia, carbohidratos_dia, grasas_dia


def verificar_restricciones(solucion, conexion_bd, calorias_objetivo, alergias):
    """Verifica si una solucion cumple con las restricciones de calorias, macronutrientes y alergias."""

    cumple_calorias = cumple_macronutrientes = cumple_alergias = True
    for dia in range(constantes.NUM_DIAS):

        calorias, proteinas, carbohidratos, grasas = calcular_datos_dia(solucion, conexion_bd, dia)

        if ag_moead.restriccion_calorias(calorias, calorias_objetivo) > 0:
            cumple_calorias = False
        if ag_moead.restriccion_macronutrientes(proteinas, carbohidratos, grasas) > 0:
            cumple_macronutrientes = False
        if any(ag_moead.restriccion_alergia(conexion_bd[int(solucion[dia * constantes.NUM_ALIMENTOS_DIARIO + i])], alergias) > 0 
               for i in range(constantes.NUM_ALIMENTOS_DIARIO)):
            cumple_alergias = False

    return {'cumple_restriccion_calorias': cumple_calorias, 'cumple_restriccion_macronutrientes': cumple_macronutrientes, 'cumple_restriccion_alergia': cumple_alergias}


def procesar_solucion(solucion, conexion_bd, calorias_objetivo, gustos, disgustos, alergias):
    """Calcula el fitness y verifica restricciones para una solucion. Devuelve diccionario para JSON"""

    fitness_calorias = calcular_fitness_acumulado(solucion, conexion_bd, calorias_objetivo, ag_moead.objetivo_calorias)
    fitness_macronutrientes = calcular_fitness_acumulado(solucion, conexion_bd, None, ag_moead.objetivo_macronutrientes)
    fitness_preferencia = calcular_fitness_preferencia(solucion, conexion_bd, gustos, disgustos)
    
    restricciones_cumplidas = verificar_restricciones(solucion, conexion_bd, calorias_objetivo, alergias)
    
    return {
        'solucion': '[' + ', '.join(map(str, solucion)) + ']',
        'fitness': [fitness_calorias, fitness_macronutrientes, fitness_preferencia],
        'verificacion': restricciones_cumplidas
    }


def ejecutar_y_guardar_resultados():
    """Ejecuta el algoritmo genetico para cada sujeto y cada seed.
    Calcula resultados y soluciones factibles.
    Guarda resultados en JSON."""

    conexion_bd = database.conexion_comida_basedatos()
    sujetos = cargar_sujetos()

    resultados_finales = []
    tiempos_totales = []
    total_de_soluciones = 0
    total_soluciones_exitosas = 0

    # Itera cada sujeto
    for indice_sujeto, sujeto in enumerate(sujetos, start=1):
        calorias_objetivo = sujeto['calorias']
        gustos = sujeto['gustos']
        disgustos = sujeto['disgustos']
        alergias = sujeto['alergias']

        # Diccionario para almacenar resultados de cada sujeto
        resultados_sujeto = {
            'sujeto_id': indice_sujeto,  
            'calorias': calorias_objetivo,
            'edad': sujeto['edad'],
            'alergias': '[' + ', '.join(alergias) + ']',  
            'gustos': '[' + ', '.join(gustos) + ']',      
            'disgustos': '[' + ', '.join(disgustos) + ']', 
            'soluciones_por_seed': [],
            'tiempo_medio_ejecucion': 0,
            'total_soluciones': 0,
            'soluciones_que_cumplen_objetivos': 0  
        }

        tiempos_ejecucion = []
        soluciones_sujeto = 0
        soluciones_exitosas_sujeto = 0

        # Itera cada seed
        for seed in constantes.SEEDS:

            # Ejecuta algoritmo
            resultado = ag_moead.ejecutar_algoritmo_genetico(
                conexion_bd, calorias_objetivo, sujeto['edad'], alergias, gustos, disgustos, seed
            )
            tiempo = resultado.exec_time
            tiempos_ejecucion.append(tiempo)

            # Diccionario para almacenar resultados de cada seeed
            soluciones_por_seed = {
                'seed': seed,
                'tiempo_ejecucion': f"{tiempo:.2f}",
                'soluciones': [],
                'num_soluciones': 0,
                'genero_soluciones': False,
                'soluciones_que_cumplen_objetivos': 0
            }

            if resultado.X is not None and len(resultado.X) > 0:
                soluciones_por_seed['genero_soluciones'] = True

                # Itera cada solucion
                for solucion in resultado.X.tolist():
                    solucion_info = procesar_solucion(
                        solucion, conexion_bd, calorias_objetivo, gustos, disgustos, alergias
                    )
                    soluciones_por_seed['soluciones'].append(solucion_info)

                    
                    if (solucion_info['verificacion']['cumple_restriccion_calorias'] and
                        solucion_info['verificacion']['cumple_restriccion_macronutrientes'] and
                        solucion_info['verificacion']['cumple_restriccion_alergia']):
                        soluciones_por_seed['soluciones_que_cumplen_objetivos'] += 1
                        soluciones_exitosas_sujeto += 1
                        total_soluciones_exitosas += 1

                soluciones_por_seed['num_soluciones'] = len(soluciones_por_seed['soluciones'])
                soluciones_sujeto += soluciones_por_seed['num_soluciones']
                total_de_soluciones += soluciones_por_seed['num_soluciones']

            resultados_sujeto['soluciones_por_seed'].append(soluciones_por_seed)

        # Añade a JSON resultados
        tiempo_medio_ejecucion = np.mean(tiempos_ejecucion)
        tiempos_totales.append(tiempo_medio_ejecucion)
        resultados_sujeto['tiempo_medio_ejecucion'] = f"{tiempo_medio_ejecucion:.2f}"
        resultados_sujeto['total_soluciones'] = soluciones_sujeto
        resultados_sujeto['soluciones_que_cumplen_objetivos'] = soluciones_exitosas_sujeto
        resultados_finales.append(resultados_sujeto)

    tiempo_medio_total = np.mean(tiempos_totales)

    # Resultados que se guardan en JSON
    resultados_a_guardar = {
        'descripcion': "Cruce : TwoPointCrossover , 0.9 --- Mutacion : 1/77 --- Algoritmo : MOEAD --- n_neighbors : 30 --- prob_neighbor_mating : 0.9 --- incremental(18)",
        'resultados': resultados_finales,
        'tiempo_medio_total': f"{tiempo_medio_total:.2f}",
        'total_soluciones': total_de_soluciones,
        'total_soluciones_cumplen_objetivos': total_soluciones_exitosas
    }

    # Guardar los resultados en un archivo JSON
    ruta_resultados = 'PYTHON/resultados/resultados_variacion_algoritmo/ag_moead/direcciones_referencia/incremental/direcciones_referencia_alta.json'
    os.makedirs(os.path.dirname(ruta_resultados), exist_ok=True)
    with open(ruta_resultados, 'w') as archivo_json:
        json.dump(resultados_a_guardar, archivo_json, indent=4)

    print(f"Archivo JSON de resultados guardado con éxito en {ruta_resultados}")


def calcular_fitness_acumulado(solucion, conexion_bd, calorias_objetivo, funcion_objetivo):
    """Calcula la desviación total de calorías o macronutrientes de una solucion"""

    total_desviacion = 0
    for dia in range(constantes.NUM_DIAS):
        calorias, proteinas, carbohidratos, grasas = calcular_datos_dia(solucion, conexion_bd, dia)

        if funcion_objetivo == ag_moead.objetivo_calorias:
            total_desviacion += funcion_objetivo(calorias, calorias_objetivo)
        elif funcion_objetivo == ag_moead.objetivo_macronutrientes:
            total_desviacion += funcion_objetivo(proteinas, carbohidratos, grasas)

    return total_desviacion


def calcular_fitness_preferencia(solucion, conexion_bd, gustos, disgustos):
    """Calcula y devuelve la penalizacion total por preferencia"""

    return sum(
        ag_moead.objetivo_preferencia_grupo(conexion_bd[int(alimento)], gustos, disgustos) 
        for alimento in solucion
    )


if __name__ == "__main__":
    ejecutar_y_guardar_resultados()