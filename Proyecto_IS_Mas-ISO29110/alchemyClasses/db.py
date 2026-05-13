import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

##print("USUARIO:", os.getenv("DB_USER"))
##print("PASSWORD:", os.getenv("DB_PASSWORD")) ESTOS PRINTS IMPRIMEN CREDENCIALES, LOS COMENTÉ POR SI QUIEREN HACER PRUEBAS USTEDES Y SEPAN DONDE PONER ESTOS PRINTS, O SEA, AQUI 

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database='BD_CURSO_IDIOMAS'
    )