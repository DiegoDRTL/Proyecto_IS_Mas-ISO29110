from alchemyClasses.db import get_connection


def get_user(nombre_usuario):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Usuario WHERE nombre_usuario = %s", (nombre_usuario,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def verify_user(nombre_usuario, contrasena):
    user = get_user(nombre_usuario)
    if user and user['contrasena'] == contrasena:
        return user
    return None


def create_user(nombre_usuario, contrasena, rol):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Usuario (nombre_usuario, contrasena, rol) VALUES (%s, %s, %s)",
            (nombre_usuario, contrasena, rol)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def user_exists(nombre_usuario):
    return get_user(nombre_usuario) is not None


def user_exists(nombre_usuario):
    return get_user(nombre_usuario) is not None


#Parte para Caso Uso: Eliminar Profesor

def obtener_profesor():
    conn = get.connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_usuario, nombre, apellido_paterno, apellido_materno
        FROM USUARIO 
        WHERE rol = 'profesor' 
    """)

    profesores = cursor.fetchall()
    cursor.close()
    conn.close()
    return profesores

def eliminar_usuario(id_usuario):
    conn = get.connection()
    cursor = conn.cursor(dictionary=True)
    try: 
        cursor.execute("""
            DELETE FROM USUARIO 
            WHERE id_usuario = %s 
        """, (id_usuario,))
        conn.commit()
        return True 
    except Exception as e:
        print("ERROR:", e)
        conn.rollback()
        return False
    finally: 
        cursor.close()
        conn.close()