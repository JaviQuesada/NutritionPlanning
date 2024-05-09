from database import conexion_comida_basedatos
from algoritmo_genetico import ejecutar_algoritmo_generico


def main():

    comida_basedatos = conexion_comida_basedatos()
    calorias = calcular_calorias()

    ejecutar_algoritmo_generico(comida_basedatos, calorias)

    print(f"Tu consumo calórico objetivo diario es: {calorias:.2f} calorias")



def calcular_calorias():
    
    # Datos del usuario
    
    peso = float(input("Introduce tu peso en kg: "))
    altura = float(input("Introduce tu altura en cm: "))
    edad = int(input("Introduce tu edad: "))
    genero = input("Introduce tu género (hombre/mujer): ")
    print("""
          1. Sedentario (poco o ningún ejercicio)
          2. Poco activo (ejercicio ligero/deportes 1-3 días a la semana)
          3. Moderadamente activo (ejercicio moderado/deportes 3-5 días a la semana)
          4. Activo (ejercicio duro/deportes 6-7 días a la semana)
          5. Muy activo (ejercicio muy duro/deportes y un trabajo físico)
          """)
    nivel_actividad = int(input("Elige tu nivel de actividad (1-5): "))

    factores_actividad = [1.2, 1.375, 1.55, 1.725, 1.9]

    if genero.lower() == 'hombre':
        bmr = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
    else:
        bmr = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

    calorias_ajustadas = bmr * factores_actividad[nivel_actividad-1]

    return calorias_ajustadas          



if __name__ == "__main__":
    main()
    