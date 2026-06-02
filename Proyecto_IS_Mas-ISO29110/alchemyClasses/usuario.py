"""
Modelos de usuarios

Este Modelo incluye todas las funciones que mandan a llamar los controladores de usuario
"""
from alchemyClasses.db import get_connection


def get_user(id_usuario):
    """
    Dado el Id de un usuario regresa toda la informacion de ese usuario
    
    Args:
        id_usuario (int): Clave primaria del Usuario del cual se obtendra la informacion.

    Returns:
        Response: La informacion del usuario en formato de diccionario.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_rol_usuarios():
    """
    Obtiene de la BD todas la ocurrencias con rol de usuario

    Returns:
        Response: La informacion de los usuarios en formato de diccionario.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USUARIO WHERE rol = 'usuario'")
    usuarios = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuarios

def verify_user(identificador, contrasena_ingresada):
    """
    Busca al usuario por su ID o por su correo directamente en la tabla USUARIO y comprueba si su
    contraseña conincide con la ingresada en la BD.
    
    Args:
        identificador (int, str): Clave primaria o correo del Usuario del cual se obtendra la informacion.
        contrasena_ingresada (str): Cadena de texto con la contraseña del usuario

    Returns:
        Response: En caso de coincidir las contraseñas manda la informacion del usuario en
                  formato de diccionario, en caso contrario regresa None.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
                SELECT id_usuario, nombre, contraseña AS contrasena, rol, correo, telefono
                FROM USUARIO
                WHERE id_usuario = %s OR correo = %s \
                """
        cursor.execute(query, (identificador, identificador))
        user = cursor.fetchone()

        # Validamos de forma segura usando la clave 'contrasena'
        if user and user['contrasena'] == contrasena_ingresada:
            try:
                query_auditoria = """
                                  INSERT INTO SESION (id_usuario, status)
                                  VALUES (%s, 'Inició Sesión en el Sistema')
                                      ON DUPLICATE KEY UPDATE
                                                           status = 'Inició Sesión en el Sistema',
                                                           ultima_conexion = CURRENT_TIMESTAMP \
                                  """
                cursor.execute(query_auditoria, (user['id_usuario'],))
                conn.commit()
            except Exception as ex_auditoria:
                print(f"No se pudo guardar el log de inicio de sesión: {ex_auditoria}")

            return user

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
    """
    Con los valores ingresados registra en la base de datos a un nuevo usuario.
    Regresa el Id con el que quedo registrado en caso de exito

    Args:
        nombre_usuario(str): Nombre con el que se registra el usuario
        a_paterno (str): Apellido paterno del usuario
        a_materno (str): Apellido materno del usuario
        contrasena (str): Contraseña con la que queda registrado el usuario
        f_nacimiento (date): Fecha de nacimiento en su formato MM/DD/AAAA
        rol (str): Rol con el que se registra el usuario
        correo (str): correo que inserto el usuario
        telefono (str): Telefono que inserto el usuario

    Returns:
        Response: En caso de exito regresa el ID registrado en la BD, en otro caso regresa False.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ====================================================================
        # 1. INSERTAR EN USUARIO (Ahora con columnas de correo y teléfono)
        # ====================================================================
        cursor.execute(
            """
            INSERT INTO USUARIO
            (nombre, apellido_paterno, apellido_materno,
             contraseña, fecha_nacimiento, rol, correo, telefono)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                nombre_usuario,
                a_paterno,
                a_materno,
                contrasena,
                f_nacimiento,
                rol,
                correo,
                telefono
            )
        )

        id_usuario = cursor.lastrowid

        # ====================================================================
        # 2. INSERTAR SEGÚN EL ROL (Especialización)
        # ====================================================================
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

        # ====================================================================
        # 3. Registra en auditoria la accion realizada (visible para el Administrador)
        # ====================================================================
        try:
            registrar_auditoria_sesion(id_usuario, f"Creó un nuevo usuario con rol '{rol}'")
        except Exception as e_auditoria:
            print(f"Advertencia al registrar auditoría: {e_auditoria}")

        return id_usuario

    except Exception as e:
        print("ERROR DE SQL EN create_user:", e)
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()

def correo_exists(correo):
    """
    Comprueba si el correo ingresado ya se encuentra registrado por otro usuario

    Args:
        Correo (str): Direccion de correo para comprobar si existe en la BD.

    Returns:
        Response: Regresa True en caso de haber encontrado un usuario con el correo ingresado
        False en otro caso.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Buscamos el correo directamente en la tabla unificada USUARIO
        cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s", (correo,))
        user = cursor.fetchone()
        return user is not None
    finally:
        cursor.close()
        conn.close()

def deleate_user(id_usuario):
    """
    Dado un ID de usuario se elimina toda la informacion del usuario en cuestion

    Args:
        id_usuario (int): Clave primaria del Usuario del cual se eliminara su informacion.

    Returns:
        Response: True si se pudo eliminar de la BD, False en otro caso.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        registrar_auditoria_sesion(id_usuario, "Eliminó el registro completo del usuario")
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
    """
    Actualiza el rol de un usuario por uno nuevo.

    Args:
        id_usuario (int): Clave primaria del Usuario al cual se le cambiara su rol.
        rol (str): Cadena de texto con el nuevo rol que se va a asignar.

    Returns:
        Response: True si se pudo cambiar el rol del usuario objetivo
                  False en caso contrario.
    """
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
    """
    Comprueba si ya existe un usuario con el mismo nombre que se ingresa

    Args:
        nombre_usuario (str): Nombre del usuario para verificar si ya existe alguien con ese nombre en la BD

    Returns:
        Response: True en caso de encontrar alguna coincidencia, False en caso contrario.
    """
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
    """
    Regresa toda la informacion de los usuario con el rol Profesor

    Returns:
        Response: La informacion de los profesores en formato de diccionario.
    """
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
    """
    Dado un ID de usuario se elimina toda la informacion del usuario en cuestion

    Args:
        id_usuario (int): Clave primaria del Usuario a eliminar.

    Returns:
        Response: True en caso de eliminar con exito al usuario de la BD, False en caso contrario.
    """
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
    """
    Actualiza el estado de la sesión registrando el ingreso al sistema.
    
    Args:
        id_usuario (int): Clave primaria del Usuario que inicio sesion.

    Returns:
        Response: True en caso de registrar el inicio de sesion en la BD, False en caso contrario.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # En lugar de 'activo', guardamos la acción de auditoría directamente en status
        query = """
        INSERT INTO SESION (id_usuario, status)
        VALUES (%s, 'Inició Sesión')
        ON DUPLICATE KEY UPDATE
            status = 'Inició Sesión',
            ultima_conexion = CURRENT_TIMESTAMP \
                """
        cursor.execute(query, (id_usuario,))
        conn.commit()
        return True
    except Exception as e:
        print("ERROR EN registrar_inicio_sesion:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def registrar_cierre_sesion(id_usuario):
    """
    Cambia el estado de la sesión en la base de datos al salir del sistema.
    
    Args:
        id_usuario (int): Clave primaria del Usuario que cerro sesion.

    Returns:
        Response: True en caso de registrar em la BD el cierre de sesion, False en caso contrario.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Registramos explícitamente la acción de salida en la columna status
        query = """
            UPDATE SESION
            SET status = 'Cerró Sesión de forma segura',
                ultima_conexion = CURRENT_TIMESTAMP
            WHERE id_usuario = %s \
                """
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
    """
    Recupera los últimos usuarios registrados que interactuaron con el sistema.
    
    Args:
        limite (int): Cantidad maxima de usuarios a los que se les va a obtener la informacion.

    Returns:
        Response: Diccionario con los ultimos 4 usuarios que interactuaron con el sistema.
    """
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
    """
    Se obtiene la informacion de todos los usuario registrados en el sistema

    Returns:
        Response: Diccionario con la informacion de todos los usuarios en el sistema.
    """

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

def actualizar_rol_usuario(id_usuario, nuevo_rol, id_admin=None):
    """
    Actualiza el rol de un usuario por uno nuevo.
    Además registra la acción realizada por el administrador.

    Args:
        id_usuario (int): Clave primaria del Usuario al cual se le cambiara su rol.
        nuevo_rol (str): Cadena de texto con el nuevo rol que se va a asignar.
        id_admin (int): Clave primaria del Administrador que realiza la accion

    Returns:
        Response: True si se pudo cambiar el rol del usuario objetivo
                  False en caso contrario.
    """

    if not nuevo_rol:
        return False

    nuevo_rol = str(nuevo_rol).strip().lower()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # Obtener información del usuario
        cursor.execute("""
            SELECT nombre, apellido_paterno, apellido_materno, rol
            FROM USUARIO
            WHERE id_usuario = %s
        """, (id_usuario,))

        usuario_afectado = cursor.fetchone()

        if not usuario_afectado:
            return False

        nombre_completo = (
            f"{usuario_afectado['nombre']} "
            f"{usuario_afectado['apellido_paterno']} "
            f"{usuario_afectado['apellido_materno']}"
        ).strip()

        rol_actual = usuario_afectado['rol']

        # Si es profesor y tiene cursos asignados no permitimos el cambio
        if rol_actual == 'profesor' and nuevo_rol != 'profesor':

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM CURSO
                WHERE id_usuario = %s
            """, (id_usuario,))

            total_cursos = cursor.fetchone()['total']

            if total_cursos > 0:
                print("No se puede cambiar el rol: el profesor tiene cursos asignados")
                return False

        # Eliminar al usuario de todas las tablas de roles
        cursor.execute(
            "DELETE FROM ALUMNO WHERE id_usuario = %s",
            (id_usuario,)
        )

        cursor.execute(
            "DELETE FROM PROFESOR WHERE id_usuario = %s",
            (id_usuario,)
        )

        cursor.execute(
            "DELETE FROM ADMINISTRADOR WHERE id_usuario = %s",
            (id_usuario,)
        )

        # Insertarlo en la tabla correspondiente al nuevo rol
        if nuevo_rol == 'alumno':
            cursor.execute(
                "INSERT INTO ALUMNO (id_usuario) VALUES (%s)",
                (id_usuario,)
            )

        elif nuevo_rol == 'profesor':
            cursor.execute(
                "INSERT INTO PROFESOR (id_usuario) VALUES (%s)",
                (id_usuario,)
            )

        elif nuevo_rol == 'administrador':
            cursor.execute(
                "INSERT INTO ADMINISTRADOR (id_usuario) VALUES (%s)",
                (id_usuario,)
            )

        else:
            print("Rol inválido")
            return False

        # Actualizar rol en la tabla USUARIO
        cursor.execute("""
            UPDATE USUARIO
            SET rol = %s
            WHERE id_usuario = %s
        """, (nuevo_rol, id_usuario))

        # Registrar acción en la auditoría
        id_log_dueno = id_admin if id_admin else id_usuario
        mensaje_detalle = f"Modificó el rol de {nombre_completo} a '{nuevo_rol}'"

        query_auditoria = """
            INSERT INTO SESION (id_usuario, status)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                status = %s,
                ultima_conexion = CURRENT_TIMESTAMP
        """

        cursor.execute(
            query_auditoria,
            (id_log_dueno, mensaje_detalle, mensaje_detalle)
        )

        conn.commit()
        return True

    except Exception as e:
        print("ERROR EN actualizar_rol_usuario:", e)
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()

def registrar_auditoria_sesion(id_usuario, accion_detalle):
    """
    Guarda la acción detallada aprovechando el nuevo tamaño VARCHAR(255).
    
    Args:
        id_usuario (int): Clave primaria del Usuario que realizo una accion en el sistema.
        accion_detalle (str): Accion que realizo el usuario

    Returns:
        Response: True en caso de registrar en la BD la accion del usuario, False en caso contrario.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:

        query = """
            INSERT INTO SESION (id_usuario, status)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                status = %s,
                ultima_conexion = CURRENT_TIMESTAMP \
                """
        cursor.execute(query, (id_usuario, accion_detalle, accion_detalle))
        conn.commit()
        return True
    except Exception as e:
        print("ERROR EN registrar_auditoria_sesion:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def obtener_logs_auditoria(limite=15):
    """
    Recupera la bitácora unificada definitiva garantizando la visibilidad
    y orden de sesiones, creación de cursos y registros de usuarios.

    Args:
        limite (int): Cantidad maxima de usuarios a los que se les va a obtener la informacion.

    Returns:
        Response: Diccionario con las ultimas 15 acciones realizadas en el sistema.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT fecha, usuario, accion
            FROM (
                         -- Sesiones y movimientos administrativos activos en tiempo real
                (
                SELECT
                    s.ultima_conexion AS fecha,
                    CONCAT(u.nombre, ' ', u.apellido_paterno, ' ', u.apellido_materno, ' (', UPPER(u.rol), ')') AS usuario,
                    s.status AS accion,
                    s.ultima_conexion AS fecha_orden,
                        0 AS tipo_evento
                    FROM SESION s
                    JOIN USUARIO u ON s.id_usuario = u.id_usuario
                )
                UNION ALL
                    -- Creación de cursos por profesores
                (
                SELECT
                    COALESCE((SELECT max(s2.ultima_conexion) FROM SESION s2 WHERE s2.id_usuario = c.id_usuario), CURRENT_TIMESTAMP) AS fecha,
                    CONCAT(u.nombre, ' ', u.apellido_paterno, ' ', u.apellido_materno, ' (', UPPER(u.rol), ')') AS usuario,
                    CONCAT('Creó el nuevo curso de idiomas: "', c.nombre, '"') AS accion,
                    COALESCE((SELECT max(s2.ultima_conexion) FROM SESION s2 WHERE s2.id_usuario = c.id_usuario), CURRENT_TIMESTAMP) AS fecha_orden,
                         1 AS tipo_evento
                         FROM CURSO c
                         JOIN USUARIO u ON c.id_usuario = u.id_usuario
                )
                UNION ALL
                 -- Registro de nuevos usuarios (se usa una fecha base más antigua si no hay sesión para no saturar el tope)
                 (
                 SELECT
                    COALESCE((SELECT s3.ultima_conexion FROM SESION s3 WHERE s3.id_usuario = u.id_usuario LIMIT 1), CAST('2026-01-01 00:00:00' AS DATETIME)) AS fecha,
                    CONCAT(u.nombre, ' ', u.apellido_paterno, ' ', u.apellido_materno, ' (', UPPER(u.rol), ')') AS usuario,
                    CONCAT('Se registró en el sistema con el rol de "', UPPER(u.rol), '"') AS accion,
                    COALESCE((SELECT s3.ultima_conexion FROM SESION s3 WHERE s3.id_usuario = u.id_usuario LIMIT 1), CAST('2026-01-01 00:00:00' AS DATETIME)) AS fecha_orden,
                        2 AS tipo_evento
                    FROM USUARIO u
                )
                ) AS bitacora_unificada
        
                -- ordenamos por la fecha del evento (lo más reciente arriba).
                -- En caso de empates de minutos o fechas simuladas, el tipo de evento desempata (Sesiones > Cursos > Registros).
                ORDER BY
                    DATE_FORMAT(fecha_orden, '%Y-%m-%d %H:%i') DESC,
                    tipo_evento ASC,
                    fecha_orden DESC
                    LIMIT %s \
                """
        cursor.execute(query, (limite,))
        resultados = cursor.fetchall()

        # Formateamos las fechas de forma segura para la interfaz HTML
        for r in resultados:
            if r['fecha']:
                try:
                    # Si el registro no tiene fecha real
                    if "2026-01-01" in str(r['fecha']):
                        r['fecha'] = "Histórico / Inicial"
                    else:
                        r['fecha'] = r['fecha'].strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    r['fecha'] = str(r['fecha'])

        return resultados
    except Exception as e:
        print("ERROR EN obtener_logs_auditoria TRIPLE COMPLETA:", e)
        return []
    finally:
        cursor.close()
        conn.close()