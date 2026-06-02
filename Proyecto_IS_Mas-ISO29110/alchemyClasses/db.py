"""
Conexion con la Base de datos

Este Modelo se encarga de conectar la base de datos con el sistema.
Hace uso de un archivo .env que contiene la contraseña, usuario y nombre de la BD
para guardar los secretos.
"""
import os
import mysql.connector
from dotenv import load_dotenv
# Como 'secretos.env.txt' está en la misma carpeta que 'db.py',
# la ruta base debe apuntar al directorio actual de este script.
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, 'secretos.env.txt')

# Cargamos explícitamente el archivo de entorno
load_dotenv(dotenv_path=env_path)

def get_connection():
    """
    Establece y retorna una conexión a la base de datos MySQL
    utilizando las credenciales de secretos.env.txt
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error crítico al conectar a la base de datos: {err}")
        raise err

