from alchemyClasses.db import get_connection


def get_user(id_usuario):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def verify_user(id_usuario, contrasena):
    user = get_user(id_usuario)
    if user and user['contraseña'] == contrasena:
        return user
    return None


def create_user(nombre_usuario, a_paterno, a_materno, contrasena, f_nacimiento, rol, correo, telefono):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO USUARIO (nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento, rol) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre_usuario, a_paterno, a_materno, contrasena, f_nacimiento, rol)
        )
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        id = cursor.fetchone
        cursor.execute(
            "Insert INTO CORREO_USUARIO (id_usuario, correo) VALUES (%s, %s)",
            (id, correo)
        )
        conn.commit()
        cursor.execute(
            "Insert INTO TELEFONO_USUARIO (id_usuario, telefono) VALUES (%s, %s)",
            (id, telefono)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def assign_rol(nombre_usuario, rol):
    conn = get_connection()
    cursor = conn.cursor()
    user = get_user(nombre_usuario)
    try:
        if (rol=="alumno"):
            cursor.execute(
                "INSERT INTO ALUMNO (id_usuario) VALUES (%s)",
                (user['id_usuario'])
            )
            conn.commit()
        else:
            cursor.execute(
                "INSERT INTO PROFESOR (id_usuario) VALUES (%s)",
                (user['id_usuario'])
            )
            conn.commit()
        cursor.execute(
            "UPDATE USUARIO SET rol= %s WHERE id_usuario= %s",
            (rol, user['id_usuario'])
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def user_exists(id_usuario):
    return get_user(id_usuario) is not None


def user_exists(nombre_usuario):
    return get_user(nombre_usuario) is not None