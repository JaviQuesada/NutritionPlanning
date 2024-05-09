#solucion_traducida.py
import numpy as np
# Traduce la solución del algoritmo genético a un formato de menú semanal
def traducir_solucion(solucion_genetica, food_database):

    menu_semanal = []

    for dia in range(7): # 7 dias de la semana
        menu_diario = [] 
        calorias_diarias = 0

        for comida in range(3):  # Desayuno, Almuerzo, Cena
            alimentos_comida = []

            for alimento_comida in range(2):  # Dos alimentos por comida
                id_alimento = int(solucion_genetica[dia * 6 + comida * 2 + alimento_comida])
                alimento = food_database[id_alimento]
                alimentos_comida.append((alimento["nombre"], alimento["calorias"]))
                calorias_diarias += alimento["calorias"]

            menu_diario.append(alimentos_comida)

        menu_diario.append(calorias_diarias)
        menu_semanal.append(menu_diario) 

    return menu_semanal


# Pinta el menú semanal
def print_solucion(menu_semanal):

    nombres_dia_semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

    for dia, menus in enumerate(menu_semanal):
        print(f"{nombres_dia_semana[dia]}:")

        for indice_comida, comida in enumerate(menus[:-1]):  # El último elemento es el total de calorías
            nombre_comida = ["Desayuno", "Almuerzo", "Cena"][indice_comida]
            print(f"  {nombre_comida}:")

            for alimento_nombre, alimento_calorias in comida:
                print(f"    - {alimento_nombre}: {round(alimento_calorias, 2)} calorías")

        print(f"  Total de calorías del día: {round(menus[-1], 2)}")  # Imprime el total de calorías del día
        print()

