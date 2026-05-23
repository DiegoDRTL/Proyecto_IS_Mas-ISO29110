from alchemyClasses.db import get_connection


def get_user(id_usuario):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_correo(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT correo FROM CORREO_USUARIO WHERE id_usuario = %s", (id_usuario,))
    correo = cursor.fetchone()
    cursor.close()
    conn.close()
    return correo

def get_telefono(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telefono FROM TELEFONO_USUARIO WHERE id_usuario = %s", (id_usuario,))
    telefono = cursor.fetchone()
    cursor.close()
    conn.close()
    return telefono

def get_rol_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USUARIO WHERE rol = usuario")
    usuarios = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuarios

def verify_user(id_usuario, contrasena_ingresada):
    """
    Busca al usuario en la base de datos y compara la contraseña
    en texto plano directamente para evitar el error de tamaño.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para acceder por nombre de columna
    try:
        # Buscamos al usuario por su ID o por su nombre de usuario en la tabla USUARIO
        # AJUSTAR el formato de id_usuario si es alfanumerico o string
        query = "SELECT id_usuario, contraseña, rol FROM USUARIO WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        user = cursor.fetchone()

        # Si el usuario existe y la contraseña de la BD coincide con la ingresada
        if user and user['contraseña'] == contrasena_ingresada:
            return user  # Retorna el diccionario con los datos del usuario para la sesión

        return None
    except Exception as e:
        print(f"❌ Error al verificar usuario: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_user(nombre_usuario, a_paterno, a_materno, contrasena, f_nacimiento, rol, correo, telefono):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Insertar en la tabla principal: USUARIO
        cursor.execute(
            "INSERT INTO USUARIO (nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento, rol) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre_usuario, a_paterno, a_materno, contrasena, f_nacimiento, rol)
        )

        # Recuperamos el ID que la base de datos le asignó automáticamente a este usuario
        id_usuario = cursor.lastrowid

        # 2. Insertar en la tabla multivaluada: CORREO_USUARIO
        cursor.execute(
            "INSERT INTO CORREO_USUARIO (id_usuario, correo) VALUES (%s, %s)",
            (id_usuario, correo)
        )

        # 3. Insertar en la tabla multivaluada: TELEFONO_USUARIO
        cursor.execute(
            "INSERT INTO TELEFONO_USUARIO (id_usuario, telefono) VALUES (%s, %s)",
            (id_usuario, telefono)
        )

        # SI TODO SALIÓ BIEN, HACEMOS UN SOLO COMMIT PARA GUARDAR TODO JUNTO
        conn.commit()
        return id_usuario

    except Exception as e:
        # ¡ESTA LÍNEA ES VITAL! Te dirá exactamente en la terminal de PyCharm qué falló
        print("❌ ERROR DE SQL EN create_user:", e)
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()

def correo_exists(correo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_usuario FROM CORREO_USUARIO WHERE correo = %s", (correo,))
        user = cursor.fetchone()
        return user is not None
    finally:
        cursor.close()
        conn.close()

def deleate_user(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM USUARIO WHERE id_usuario='%s'",
            (id_usuario)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def assign_rol(id_usuario, rol):
    conn = get_connection()
    cursor = conn.cursor()
    user = get_user(id_usuario)
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


def user_exists(nombre_usuario):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_usuario FROM USUARIO WHERE nombre = %s", (nombre_usuario,))
        user = cursor.fetchone()
        return user is not None
    finally:
        cursor.close()
        conn.close()


#Parte para Caso Uso: Eliminar Profesor

def obtener_profesor():
    conn = get_connection()
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
    conn = get_connection()
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
