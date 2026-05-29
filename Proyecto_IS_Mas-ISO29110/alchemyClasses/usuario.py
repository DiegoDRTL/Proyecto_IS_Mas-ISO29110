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
    cursor.execute("SELECT * FROM USUARIO WHERE rol = 'usuario'")
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
        query = "SELECT id_usuario, nombre, contraseña, rol FROM USUARIO WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        user = cursor.fetchone()

        # Si el usuario existe y la contraseña de la BD coincide con la ingresada
        if user and user['contraseña'] == contrasena_ingresada:
            return user  # Retorna el diccionario con los datos del usuario para la sesión

        return None
    except Exception as e:
        print(f"Error al verificar usuario: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_user(nombre_usuario, a_paterno, a_materno,
                contrasena, f_nacimiento,
                rol, correo, telefono):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # =========================
        # INSERTAR EN USUARIO
        # =========================
        cursor.execute(
            """
            INSERT INTO USUARIO
            (nombre, apellido_paterno, apellido_materno,
             contraseña, fecha_nacimiento, rol)

            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                nombre_usuario,
                a_paterno,
                a_materno,
                contrasena,
                f_nacimiento,
                rol
            )
        )

        id_usuario = cursor.lastrowid

        # =========================
        # INSERTAR CORREO
        # =========================
        cursor.execute(
            """
            INSERT INTO CORREO_USUARIO
            (id_usuario, correo)

            VALUES (%s, %s)
            """,
            (id_usuario, correo)
        )

        # =========================
        # INSERTAR TELEFONO
        # =========================
        cursor.execute(
            """
            INSERT INTO TELEFONO_USUARIO
            (id_usuario, telefono)

            VALUES (%s, %s)
            """,
            (id_usuario, telefono)
        )

        # =========================
        # INSERTAR SEGÚN EL ROL
        # =========================

        rol_normalizado = rol.strip().lower()

        if rol_normalizado == 'alumno':

            cursor.execute(
                """
                INSERT INTO ALUMNO (id_usuario)
                VALUES (%s)
                """,
                (id_usuario,)
            )

        elif rol_normalizado == 'profesor':

            cursor.execute(
                """
                INSERT INTO PROFESOR (id_usuario)
                VALUES (%s)
                """,
                (id_usuario,)
            )

        elif rol_normalizado == 'administrador':

            cursor.execute(
                """
                INSERT INTO ADMINISTRADOR (id_usuario)
                VALUES (%s)
                """,
                (id_usuario,)
            )

        conn.commit()

        return id_usuario

    except Exception as e:

        print("ERROR DE SQL EN create_user:", e)

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
            (id_usuario,)
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
    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM INSCRIBE
            WHERE id_usuario = %s
        """, (id_usuario,))

        cursor.execute("""
            DELETE FROM ALUMNO
            WHERE id_usuario = %s
        """, (id_usuario,))

        cursor.execute("""
            DELETE FROM PROFESOR
            WHERE id_usuario = %s
        """, (id_usuario,))

        cursor.execute("""
            DELETE FROM ADMINISTRADOR
            WHERE id_usuario = %s
        """, (id_usuario,))

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

# Control de historial
def registrar_inicio_sesion(id_usuario):
    """Crea o actualiza el estado de la sesión de un usuario a 'activo'."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
                INSERT INTO SESION (id_usuario, status)
                VALUES (%s, 'activo')
                    ON DUPLICATE KEY UPDATE status = 'activo' \
                """
        cursor.execute(query, (id_usuario,))
        conn.commit()
        return True
    except Exception as e:
        print("❌ ERROR EN registrar_inicio_sesion:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def registrar_cierre_sesion(id_usuario):
    """Cambia el estado de la sesión de un usuario a 'inactivo' al desloguearse."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE SESION SET status = 'inactivo' WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        conn.commit()
        return True
    except Exception as e:
        print("ERROR EN registrar_cierre_sesion:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def obtener_usuarios_recientes(limite=4):
    """Recupera los últimos usuarios registrados que interactuaron con el sistema."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
                SELECT u.nombre, u.rol, s.ultima_conexion
                FROM SESION s
                         JOIN USUARIO u ON s.id_usuario = u.id_usuario
                ORDER BY s.ultima_conexion DESC
                    LIMIT %s \
                """
        cursor.execute(query, (limite,))
        return cursor.fetchall()
    except Exception as e:
        print("ERROR EN obtener_usuarios_recientes:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def obtener_todos_usuarios():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT 
                id_usuario,
                nombre,
                apellido_paterno,
                apellido_materno,
                rol
            FROM USUARIO
            ORDER BY id_usuario ASC
        """)

        usuarios = cursor.fetchall()

        return usuarios

    except Exception as e:

        print("ERROR:", e)
        return []

    finally:

        cursor.close()
        conn.close()
        
def actualizar_rol_usuario(id_usuario, nuevo_rol):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # actualizar rol en USUARIO
        cursor.execute("""
            UPDATE USUARIO
            SET rol = %s
            WHERE id_usuario = %s
        """, (nuevo_rol, id_usuario))

        # eliminar de TODAS las tablas de roles
        cursor.execute("DELETE FROM ALUMNO WHERE id_usuario = %s", (id_usuario,))
        cursor.execute("DELETE FROM PROFESOR WHERE id_usuario = %s", (id_usuario,))
        cursor.execute("DELETE FROM ADMINISTRADOR WHERE id_usuario = %s", (id_usuario,))

        # insertar en la tabla correspondiente
        if nuevo_rol.lower() == 'alumno':

            cursor.execute("""
                INSERT INTO ALUMNO (id_usuario)
                VALUES (%s)
            """, (id_usuario,))

        elif nuevo_rol.lower() == 'profesor':

            cursor.execute("""
                INSERT INTO PROFESOR (id_usuario)
                VALUES (%s)
            """, (id_usuario,))

        elif nuevo_rol.lower() == 'administrador':

            cursor.execute("""
                INSERT INTO ADMINISTRADOR (id_usuario)
                VALUES (%s)
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