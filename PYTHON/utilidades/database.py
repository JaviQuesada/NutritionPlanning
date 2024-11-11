# database.py

import os
from dotenv import load_dotenv
import mysql.connector # Importacion libreria MySQL

load_dotenv()

def conexion_comida_basedatos():
    """Establece una conexión con la base de datos y obtiene los datos de la tabla 'comida'."""

    # Configuracion de la conexion a la base de datos
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'raise_on_warnings': True
    }
    
    # Establece la conexion con la base de datos
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)

    # Consulta para obtener los datos necesarios de la tabla 'comida'
    query = "SELECT nombre, grupo, calorias, grasas, proteinas, carbohidratos FROM comida"
    cursor.execute(query)
    
    # Recupera los registros obtenidos por la consulta
    comida_basedatos = cursor.fetchall()
  
    # Cierra el cursor y la conexion a la base de datos
    cursor.close()
    cnx.close()
    
    return comida_basedatos