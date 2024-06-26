# funciones_auxiliares.py

from database import conexion_comida_basedatos
from constantes import GruposComida

comida_basedatos = conexion_comida_basedatos()

def calculo_macronutrientes(calorias_diarias, proteinas, carbohidratos, grasas):
    porcentaje_proteinas = ((proteinas * 4) / calorias_diarias) * 100
    porcentaje_carbohidratos = ((carbohidratos * 4) / calorias_diarias) * 100
    porcentaje_grasas = ((grasas * 4) / calorias_diarias) * 100

    return porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas


def filtrar_comida(comida_basedatos, tipo):

    match tipo:

        case "almuerzo_cena":
            return [i for i, item in enumerate(comida_basedatos) if not item["grupo"].startswith(
            (   GruposComida.Bebidas.BEBIDAS[0],
                GruposComida.Lacteos.LecheVaca.LECHE_VACA[0][:2],
                GruposComida.Lacteos.BEBIDAS_LACTEAS[0],
                GruposComida.Azucares.AZUCARES[0])
            )and not item["grupo"].startswith(
                GruposComida.Cereales.CEREALES[0]
            )or item["grupo"] in {
                GruposComida.Cereales.ARROZ[0],
                GruposComida.Cereales.PASTA[0],
                GruposComida.Cereales.PIZZAS[0]
            }]
        
        case "bebidas":
            return [i for i, item in enumerate(comida_basedatos) if item["grupo"].startswith(
                (GruposComida.Bebidas.BEBIDAS[0],)
            )]
        
        case "desayuno":
            return [i for i, item in enumerate(comida_basedatos) if item["grupo"].startswith(
                (GruposComida.Cereales.CEREALES[0],)
            ) and item["grupo"] not in {
                GruposComida.Cereales.ARROZ[0],
                GruposComida.Cereales.PASTA[0],
                GruposComida.Cereales.PIZZAS[0]
            }]
        
        case "bebida_desayuno":
            return [i for i, item in enumerate(comida_basedatos) if item["grupo"].startswith(
                (GruposComida.Lacteos.LecheVaca.LECHE_VACA[0][:2],
                 GruposComida.Lacteos.BEBIDAS_LACTEAS[0],
                 GruposComida.Bebidas.ZUMOS[0])
            )]
        
        case "snacks":
            return [i for i, item in enumerate(comida_basedatos) if item["grupo"].startswith(
                (GruposComida.Frutas.FRUTAS[0],
                 GruposComida.Azucares.AZUCARES[0])
            )]

