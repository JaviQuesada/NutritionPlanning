from enum import Enum

# Porcentajes objetivos y límites de macronutrientes
OBJETIVO_PROTEINAS = 22.5
OBJETIVO_CARBOHIDRATOS = 55
OBJETIVO_GRASAS = 27.5

LIMITE_PROTEINAS = (10, 35)
LIMITE_CARBOHIDRATOS = (45, 65)
LIMITE_GRASAS = (20, 35)

# Factores de penalización
PENALIZACION_CALORIAS = 10
PENALIZACION_MACRONUTRIENTES = 5
PENALIZACION_PREFERENCIA = 10
PENALIZACION_ALERGIA = 100
PENALIZACION_BEBIDA = 100

# Parámetros del problema
NUM_DIAS = 7
NUM_COMIDAS = 3
NUM_ALIMENTOS_POR_COMIDA = 3
NUM_GENES = NUM_DIAS * NUM_COMIDAS * NUM_ALIMENTOS_POR_COMIDA

# Enumeraciones para supergrupos de alimentos
class Supergrupo(Enum):
    CEREALES = ("A", "Cereals and cereal products")
    LACTEOS = ("B", "Milk and milk products")
    HUEVOS = ("C", "Eggs")
    VEGETALES = ("D", "Vegetables")
    FRUTAS = ("F", "Fruit")
    NUECES_SEMILLAS = ("G", "Nuts and seeds")
    HIERBAS_ESPECIAS = ("H", "Herbs and spices")
    PESCADO = ("J", "Fish and fish products")
    CARNE = ("M", "Meat and meat products")
    GRASAS = ("O", "Fats and oils")
    BEBIDAS = ("P", "Beverages")
    ALCOHOL = ("Q", "Alcoholic beverages")
    AZUCARES = ("S", "Sugars, preserves and snacks")
    SOPAS_SALSAS = ("W", "Soups, sauces and miscellaneous foods")

    @property
    def letra(self):
        return self.value[0]

    @property
    def nombre(self):
        return self.value[1]

# Factores de actividad
class NivelActividad(Enum):
    SEDENTARIO = 1.2
    POCO_ACTIVO = 1.375
    MODERADAMENTE_ACTIVO = 1.55
    ACTIVO = 1.725
    MUY_ACTIVO = 1.9

# Nombres de días de la semana y comidas
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
COMIDAS = ["Desayuno", "Almuerzo", "Cena"]
