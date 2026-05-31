import os
import mysql.connector
from dotenv import load_dotenv

# Cargamos explícitamente el archivo de entorno
load_dotenv(env_path)

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