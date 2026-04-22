import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='usuario_prac1',
        password='Practica2!',
        database='login'
    )
