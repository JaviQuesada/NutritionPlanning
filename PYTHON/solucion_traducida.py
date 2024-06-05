#solucion_traducida.py

from constantes import NUM_DIAS, NUM_COMIDAS, NUM_ALIMENTOS_POR_COMIDA, DIAS_SEMANA, COMIDAS 
import numpy as np

# Traduce la solución del algoritmo genético a un formato de menú semanal
def traducir_solucion(solucion_genetica, food_database):

    menu_semanal = []

    for dia in range(NUM_DIAS): # 7 dias de la semana
        menu_diario = [] 
        calorias_diarias = 0

        for comida in range(NUM_COMIDAS):  # Desayuno, Almuerzo, Cena
            alimentos_comida = []

            for alimento_comida in range(NUM_ALIMENTOS_POR_COMIDA):  # Tres alimentos por comida
                id_alimento = int(solucion_genetica[dia * NUM_COMIDAS * NUM_ALIMENTOS_POR_COMIDA + comida * NUM_ALIMENTOS_POR_COMIDA + alimento_comida])
                alimento = food_database[id_alimento]
                alimentos_comida.append((alimento["nombre"], alimento["calorias"]))
                calorias_diarias += alimento["calorias"]

            menu_diario.append(alimentos_comida)

        menu_diario.append(calorias_diarias)
        menu_semanal.append(menu_diario) 

    return menu_semanal


# Pinta el menú semanal
def print_solucion(menu_semanal):

    for dia, menus in enumerate(menu_semanal):
        print(f"{DIAS_SEMANA[dia]}:")

        for indice_comida, comida in enumerate(menus[:-1]):  # El último elemento es el total de calorías
            nombre_comida = COMIDAS[indice_comida]
            print(f"  {nombre_comida}:")

            for alimento_nombre, alimento_calorias in comida:
                print(f"    - {alimento_nombre}: {round(alimento_calorias, 2)} calorías")

        print(f"  Total de calorías del día: {round(menus[-1], 2)}")  # Imprime el total de calorías del día
        print()

