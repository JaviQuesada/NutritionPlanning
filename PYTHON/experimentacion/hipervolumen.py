import json
import numpy as np
from pymoo.indicators.hv import HV
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

# Lista de archivos JSON a procesar
ARCHIVOS_JSON = [
    'PYTHON/resultados/resultados_manejo_restricciones/ag_metodo_separatista/cruce/cruce_unpunto_bajo.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_metodo_separatista/cruce/cruce_unpunto_alto.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_metodo_separatista/cruce/cruce_dospuntos_bajo.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_metodo_separatista/cruce/cruce_dospuntos_alto.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_metodo_separatista/mutacion/mutacion_media.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_metodo_separatista/mutacion/mutacion_alta.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_metodo_separatista/mutacion/mutacion_baja.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_penalizacion_estatica/cruce/cruce_unpunto_bajo.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_penalizacion_estatica/cruce/cruce_unpunto_alto.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_penalizacion_estatica/cruce/cruce_dospuntos_bajo.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_penalizacion_estatica/cruce/cruce_dospuntos_alto.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_penalizacion_estatica/mutacion/mutacion_media.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_penalizacion_estatica/mutacion/mutacion_alta.json',
    'PYTHON/resultados/resultados_manejo_restricciones/ag_penalizacion_estatica/mutacion/mutacion_baja.json'
]

# Ruta donde se guardan los resultados
RUTA_SALIDA = 'PYTHON/resultados/resultados_variacion_algoritmo/ag_moead/direcciones_referencia/incremental/hipervolumenes/hipervolumenes_moead_direcciones_referencia_incremental_baja.json'


def leer_json(ruta_archivo):
    """Lee un archivo JSON y devuelve su contenido."""

    try:
        with open(ruta_archivo, 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print(f"Error: El archivo {ruta_archivo} no existe.")
        return None


def extraer_soluciones_factibles(ruta_archivo):
    """Extrae todas las soluciones factibles de un archivo JSON."""

    datos = leer_json(ruta_archivo)
    if datos is None:
        return []

    soluciones_factibles = []
    # Itera cada sujeto
    for sujeto in datos['resultados']:

        # Itera cada seed
        for seed in sujeto['soluciones_por_seed']:
            if seed['genero_soluciones']:

                # Itera cada solucion
                for solucion in seed['soluciones']:
                    restricciones = solucion['verificacion']

                    if (restricciones['cumple_restriccion_calorias'] and
                        restricciones['cumple_restriccion_macronutrientes'] and
                        restricciones['cumple_restriccion_alergia']):
                        soluciones_factibles.append(solucion['fitness'])

    return soluciones_factibles


def extraer_soluciones_por_seed(ruta_archivo):
    """Extrae soluciones factibles agrupadas por seed."""

    datos = leer_json(ruta_archivo)
    if datos is None:
        return {}

    soluciones_por_seed = {}
    # Itera cada sujeto
    for index_sujeto, sujeto in enumerate(datos['resultados']):
        sujeto_id = f"sujeto {index_sujeto + 1}"
        soluciones_por_seed[sujeto_id] = []

        # Itera cada seed
        for seed in sujeto['soluciones_por_seed']:
            soluciones_factibles = []
            if seed['genero_soluciones']:

                # Itera cada solucion
                for solucion in seed['soluciones']:
                    restricciones = solucion['verificacion']

                    if (restricciones['cumple_restriccion_calorias'] and
                        restricciones['cumple_restriccion_macronutrientes'] and
                        restricciones['cumple_restriccion_alergia']):
                        soluciones_factibles.append(solucion['fitness'])

            # Agrega soluciones factibles por seed
            soluciones_por_seed[sujeto_id].append({
                'seed': seed['seed'],
                'soluciones_factibles': soluciones_factibles if soluciones_factibles else None
            })

    return soluciones_por_seed


def calcular_punto_referencia(archivos_json):
    """Calcula el punto de referencia usando todas las soluciones factibles."""
    todas_soluciones_factibles = []
    for archivo in archivos_json:
        todas_soluciones_factibles.extend(extraer_soluciones_factibles(archivo))

    # Punto de referencia + 10%
    soluciones_array = np.array(todas_soluciones_factibles)
    punto_referencia = np.max(soluciones_array, axis=0) * 1.1  
    print("Punto de referencia:", punto_referencia)
    return punto_referencia


def filtrar_no_dominadas(soluciones):
    """Filtra y devuelve las soluciones no dominadas."""

    if len(soluciones) == 0:
        return []
    soluciones_array = np.array(soluciones)
    nds = NonDominatedSorting()
    indices_no_dominados = nds.do(soluciones_array, only_non_dominated_front=True)
    return soluciones_array[indices_no_dominados]


def calcular_hipervolumen_por_seed(ruta_archivo, punto_referencia):
    """Calcula el hipervolumen de las soluciones no dominadas por cada seed."""

    calculo_hv = HV(ref_point=punto_referencia)

    soluciones_por_seed = extraer_soluciones_por_seed(ruta_archivo)
    hipervolumenes_por_sujeto = {}

    # Itera cada sujeto
    for sujeto_id, seeds in soluciones_por_seed.items():
        hipervolumenes_por_sujeto[sujeto_id] = []

        # Itera cada seed
        for seed in seeds:
            soluciones = seed['soluciones_factibles']

            # Filtra soluciones factibles
            if soluciones is not None and len(soluciones) > 0:
                soluciones_no_dominadas = filtrar_no_dominadas(soluciones)

                # Calcula el hipervolumen
                if len(soluciones_no_dominadas) > 0:
                    hipervolumen_actual = calculo_hv.do(soluciones_no_dominadas)
                    print(f"Hipervolumen para {sujeto_id}, Seed {seed['seed']}: {hipervolumen_actual}")
                else:
                    hipervolumen_actual = None
                    print(f"Hipervolumen para {sujeto_id}, Seed {seed['seed']}: N/A (No hay soluciones no dominadas)")
            else:
                hipervolumen_actual = None
                print(f"Hipervolumen para {sujeto_id}, Seed {seed['seed']}: N/A (No hay soluciones factibles)")

            # Agrega el hipervolumen calculado
            hipervolumenes_por_sujeto[sujeto_id].append({
                "seed": seed['seed'],
                "hipervolumen": hipervolumen_actual
            })

    return hipervolumenes_por_sujeto


def guardar_en_json(datos, ruta_salida):
    """Guarda los resultados en un archivo JSON."""

    with open(ruta_salida, 'w') as archivo:
        json.dump(datos, archivo, indent=4)
    print(f"Hipervolúmenes guardados en {ruta_salida}")


def main():
    """Función principal que calcula el punto de referencia o los hipervolumenes por seed."""

    accion = input("¿Que accion realizar? (1: Calcular punto de referencia, 2: Calcular hipervolumen por seed): ")

    if accion == "1":
        calcular_punto_referencia(ARCHIVOS_JSON)
    elif accion == "2":
        punto_referencia = calcular_punto_referencia(ARCHIVOS_JSON)
        if punto_referencia is not None:
            hipervolumenes = calcular_hipervolumen_por_seed(
                'PYTHON/resultados/resultados_variacion_algoritmo/ag_moead/direcciones_referencia/incremental/direcciones_referencia_baja.json',
                punto_referencia
            )
            guardar_en_json(hipervolumenes, RUTA_SALIDA)
    else:
        print("Opción no valida. Elige 1 o 2.")


if __name__ == "__main__":
    main()