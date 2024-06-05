#__main.py__

from database import conexion_comida_basedatos
from preguntas_usuario import calcular_calorias, preguntar_supergrupos
from algoritmo_genetico import ejecutar_algoritmo_genetico

def main():

    comida_basedatos = conexion_comida_basedatos()

    objetivo_calorico = calcular_calorias()

    supergrupo_alergia, supergrupo_gusta, supergrupo_no_gusta = preguntar_supergrupos()

    print(f"Tu consumo calórico objetivo diario es: {objetivo_calorico:.2f} calorias")

    ejecutar_algoritmo_genetico(comida_basedatos, objetivo_calorico, supergrupo_alergia, supergrupo_gusta, supergrupo_no_gusta)


if __name__ == "__main__":
    main()
    