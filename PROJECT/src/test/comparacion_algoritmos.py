import sys
import os
import json
import numpy as np
from scipy import stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../external/stac")))

# Importar las funciones necesarias de STAC
from stac.nonparametric_tests import friedman_aligned_ranks_test, shaffer_multitest

def cargar_hipervolumenes(ruta_archivo):
    """Carga los hipervolumenes desde un archivo JSON y los almacena en un diccionario."""

    with open(ruta_archivo, 'r') as f:
        datos = json.load(f)

    hipervolumenes = {}

    # Itera cada sujeto
    for sujeto in datos:
        seeds = datos[sujeto]
        for entry in seeds:
            # Valida si hipervolumen es un numero
            if isinstance(entry['hipervolumen'], (int, float)):
                hipervolumenes[(sujeto, entry['seed'])] = float(entry['hipervolumen'])
            else:
                hipervolumenes[(sujeto, entry['seed'])] = None

    return hipervolumenes

def filtrar_hipervolumenes(*hipervolumenes_list):
    """Filtra los hipervolumenes eliminando los valores None y sus correspondientes en otras listas."""

    filtrado = []

    # Recorre listas en paralelo y filtra los que no contienen None
    for valores in zip(*hipervolumenes_list):
        if None not in valores:
            filtrado.append(valores)

    resultado = []

    for i in range(len(hipervolumenes_list)):
        resultado.append([])

    for valores in filtrado:
        for i, valor in enumerate(valores):
            resultado[i].append(valor)

    return resultado

def is_better(rank_1, rank_2):
    """Determina si el primer metodo es mejor que el segundo basado en los rankings."""

    return rank_1 < rank_2

def prueba_wilcoxon(hipervolumenes_1, hipervolumenes_2, nombre_1, nombre_2):
    """Realiza la prueba de Wilcoxon entre dos conjuntos de hipervolumenes."""

    if len(hipervolumenes_1) == 0 or len(hipervolumenes_2) == 0:
        print("No hay suficientes datos para la comparacion.")
        return
    
    _, p_value = stats.wilcoxon(hipervolumenes_1, hipervolumenes_2)

    mediana_1 = np.median(hipervolumenes_1)
    mediana_2 = np.median(hipervolumenes_2)

    print("Resultado de la prueba de Wilcoxon entre " + nombre_1 + " y " + nombre_2 + ":")
    print("p-value:", p_value)
    print("Mediana de " + nombre_1 + ":", mediana_1)
    print("Mediana de " + nombre_2 + ":", mediana_2)

    if p_value >= 0.05:
        print("No hay suficiente evidencia.")
    else:
        if mediana_1 > mediana_2:
            print(nombre_1 + " es mejor que " + nombre_2)
        else:
            print(nombre_2 + " es mejor que " + nombre_1)


def friedman_y_shaffer(hipervolumenes_filtrados, nombres_archivos):
    """Realiza el test de rangos alineados de Friedman y la correccion post-hoc de Shaffer."""

    _, pv, ranks, pvts = friedman_aligned_ranks_test(*hipervolumenes_filtrados)
    print(f"p-value: {pv}")

    
    ranks_dict = {nombre: rank for nombre, rank in zip(nombres_archivos, ranks)}

    ranking_ordenado = sorted(ranks_dict.items(), key=lambda item: item[1])
    print("\nRanking de los métodos (mejor al peor):")
    for i, (nombre, rank) in enumerate(ranking_ordenado, start=1):
        print(f"{i}. {nombre}: ranking promedio = {rank:.4f}")

    if pv < 0.05:
        comparisons, _, _, adj_p_values = shaffer_multitest(ranks_dict)
        print("\nComparaciones significativas (Shaffer post-hoc):")
        for comp, apv in zip(comparisons, adj_p_values):
            cl, cr = comp.split(" vs ")
            if apv < 0.05:
                if is_better(ranks_dict[cl], ranks_dict[cr]):
                    print(f"{cl} es mejor que {cr} (p-valor ajustado: {apv:.4f})")
                else:
                    print(f"{cr} es mejor que {cl} (p-valor ajustado: {apv:.4f})")
            else:
                print(f"{cl} y {cr} no muestran diferencia significativa (p-valor ajustado: {apv:.4f})")
    else:
        print("\nNo hay suficiente evidencia para rechazar la hipótesis nula.")

def main():
    """Realiza comparaciones 1vs1 o NvsN."""
    tipo_comparacion = input("Que tipo de comparacion deseas realizar?\n1: Comparacion 1vs1 usando Wilcoxon\n2: Comparacion NvsN usando Friedman con Shaffer\nIntroduce 1 o 2: ")

    if tipo_comparacion == "1":
        archivo_1 = input("Introduce la ruta del archivo 1 (JSON): ")
        archivo_2 = input("Introduce la ruta del archivo 2 (JSON): ")
        hipervolumenes_1 = cargar_hipervolumenes(archivo_1)
        hipervolumenes_2 = cargar_hipervolumenes(archivo_2)
        hipervolumenes_1_filtrado, hipervolumenes_2_filtrado = filtrar_hipervolumenes(
            list(hipervolumenes_1.values()), list(hipervolumenes_2.values()))
        prueba_wilcoxon(hipervolumenes_1_filtrado, hipervolumenes_2_filtrado, archivo_1, archivo_2)

    elif tipo_comparacion == "2":
        archivos = []
        while True:
            archivo = input("Introduce la ruta del archivo (JSON) o escribe 'n' para terminar: ")
            if archivo.lower() == 'n':
                break
            archivos.append(archivo)
        hipervolumenes = []
        for archivo in archivos:
            datos = cargar_hipervolumenes(archivo)
            valores = list(datos.values())
            hipervolumenes.append(valores)
        hipervolumenes_filtrados = filtrar_hipervolumenes(*hipervolumenes)
        friedman_y_shaffer(hipervolumenes_filtrados, archivos)

    else:
        print("Opcion no valida.")

if __name__ == "__main__":
    main()