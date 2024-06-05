# preguntas_usuario.py

from database import conexion_comida_basedatos
from constantes import NivelActividad, Supergrupo

comida_basedatos = conexion_comida_basedatos()

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
    
    factores_actividad = [nivel.value for nivel in NivelActividad]

    if genero.lower() == 'hombre':
        tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
    else:
        tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

    calorias_ajustadas = tmb * factores_actividad[nivel_actividad-1]

    return calorias_ajustadas


def preguntar_supergrupos():

    supergrupos = [(sg.letra, sg.nombre) for sg in Supergrupo]

    print("Supergrupos disponibles:")

    for i, (letra, nombre) in enumerate(supergrupos):
        print(f"{i+1}. {letra} - {nombre}")

    supergrupo_alergia = int(input("Hay alguna categoría de alimento que no puedas comer o presente algún tipo de alergia (1-{}): ".format(len(supergrupos))))
    supergrupo_gusta = int(input("Elige tu supergrupo favorito (1-{}): ".format(len(supergrupos))))
    supergrupo_no_gusta = int(input("Elige el supergrupo que menos te gusta (1-{}): ".format(len(supergrupos))))

    return supergrupos [supergrupo_alergia-1], [supergrupo_gusta-1], supergrupos[supergrupo_no_gusta-1]