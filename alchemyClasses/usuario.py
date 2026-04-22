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