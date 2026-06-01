import mysql.connector
import os

from dotenv import load_dotenv

# Ruta absoluta al .env que está al nivel de app.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Cargar variables de entorno
load_dotenv(ENV_PATH)

def get_connection():
    """
    Establece y retorna una conexión a MySQL
    usando las variables definidas en .env
    """

    try:

        print("DB_NAME:", os.getenv('DB_NAME'))

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