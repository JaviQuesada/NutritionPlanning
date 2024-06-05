# funciones_auxiliares.py

from database import conexion_comida_basedatos
from constantes import LIMITE_PROTEINAS, LIMITE_CARBOHIDRATOS, LIMITE_GRASAS

comida_basedatos = conexion_comida_basedatos()

def calculo_macronutrientes(calorias_diarias, proteinas, carbohidratos, grasas):
    porcentaje_proteinas = ((proteinas * 4) / calorias_diarias) * 100
    porcentaje_carbohidratos = ((carbohidratos * 4) / calorias_diarias) * 100
    porcentaje_grasas = ((grasas * 4) / calorias_diarias) * 100

    return porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas


