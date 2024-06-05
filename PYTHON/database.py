# database.py

import os
from dotenv import load_dotenv
import mysql.connector # Importación librería MySQL

load_dotenv()
# Establece conexión y obtiene resultados
def conexion_comida_basedatos():

    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'raise_on_warnings': True
    }
    
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    
    query = "SELECT nombre, grupo, calorias, grasas, proteinas, carbohidratos, supergrupo, supergrupo_nombre FROM comida"
    cursor.execute(query)
    
    comida_basedatos = cursor.fetchall()
  
    cursor.close()
    cnx.close()
    
    return comida_basedatos


# Función para establecer conexión y obtener resultados de la base de datos
def conexion_supergrupo():
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'raise_on_warnings': True
    }
    
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    
    query = "SELECT DISTINCT supergrupo, supergrupo_nombre FROM comida"
    cursor.execute(query)
    
    supergrupos = cursor.fetchall()
  
    cursor.close()
    cnx.close()
    
    # Ordenar alfabéticamente por el nombre del supergrupo
    supergrupos_ordenados = sorted(supergrupos, key=lambda x: x['supergrupo_nombre'])
    
    return supergrupos_ordenados