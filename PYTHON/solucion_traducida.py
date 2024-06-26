#solucion_traducida.py

from constantes import *
import numpy as np

def traducir_solucion(solucion, comida_basedatos):
    menu = []
    indice = 0

    for dia in DIAS_SEMANA:
        dia_menu = {"dia": dia, "comidas": [], "calorias_dia": 0}
        for comida in COMIDAS:
            comida_detalle = {"nombre": comida["nombre"], "alimentos": [], "calorias_comida": 0}
            for _ in range(comida["num_alimentos"]):
                alimento = comida_basedatos[int(solucion[indice])]
                comida_detalle["alimentos"].append(alimento["nombre"])
                comida_detalle["calorias_comida"] += alimento["calorias"]
                dia_menu["calorias_dia"] += alimento["calorias"]
                indice += 1
            dia_menu["comidas"].append(comida_detalle)
        menu.append(dia_menu)
    
    return menu

def mostrar_menu(menu):
    for dia_menu in menu:
        print(f"{dia_menu['dia']} (Calorías totales: {dia_menu['calorias_dia']}):")
        for comida in dia_menu["comidas"]:
            alimentos = "\n    - ".join(comida["alimentos"])
            print(f"  {comida['nombre']} (Calorías: {comida['calorias_comida']}): \n    - {alimentos}")
        print("-" * 40)

