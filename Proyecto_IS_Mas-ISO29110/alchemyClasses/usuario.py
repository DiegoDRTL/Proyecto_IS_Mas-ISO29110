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
    Busca al usuario en la base de datos, compara la contraseña
    e inserta de forma automática el log de auditoría en la tabla SESION.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para acceder por nombre de columna
    try:
        # Buscamos al usuario por su ID o por su nombre de usuario en la tabla USUARIO
        query = "SELECT id_usuario, nombre, contraseña, rol FROM USUARIO WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        user = cursor.fetchone()

        # Si el usuario existe y la contraseña de la BD coincide con la ingresada
        if user and user['contraseña'] == contrasena_ingresada:

            # REGISTRO DE AUDITORÍA
            try:
                # Usamos una consulta directa para no romper el cursor actual
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
                # No hacemos return False aquí para que el usuario sí pueda entrar al sistema incluso si falla el registro de la auditoria
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
        registrar_auditoria_sesion(id_usuario, f"Creó un nuevo usuario con rol '{rol}'")
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
    """Actualiza el estado de la sesión registrando el ingreso al sistema."""
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
        print("❌ ERROR EN registrar_inicio_sesion:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def registrar_cierre_sesion(id_usuario):
    """Cambia el estado de la sesión en la base de datos al salir del sistema."""
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
        print("❌ ERROR EN registrar_cierre_sesion:", e)
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

def actualizar_rol_usuario(id_usuario, nuevo_rol, id_admin=None):
    if not nuevo_rol:
        return False
    nuevo_rol = str(nuevo_rol).strip().lower()

    conn = get_connection()
    # Usamos dictionary=True para poder leer de forma limpia el nombre del afectado
    cursor = conn.cursor(dictionary=True)

    try:
        # OBTENER EL NOMBRE COMPLETO ANTES DE HACER CAMBIOS
        cursor.execute("""
                       SELECT nombre, apellido_paterno, apellido_materno
                       FROM USUARIO WHERE id_usuario = %s
                       """, (id_usuario,))
        usuario_afectado = cursor.fetchone()

        if usuario_afectado:
            nombre_completo = f"{usuario_afectado['nombre']} {usuario_afectado['apellido_paterno']} {usuario_afectado['apellido_materno']}".strip()
        else:
            nombre_completo = f"ID {id_usuario}"

        # Actualizar rol en la tabla USUARIO
        cursor.execute("""
                       UPDATE USUARIO
                       SET rol = %s
                       WHERE id_usuario = %s
                       """, (nuevo_rol, id_usuario))

        # En lugar de eliminar físicamente rompiendo restricciones FK, insertamos con IGNORE
        # en la nueva tabla de especialización correspondiente.
        if nuevo_rol == 'alumno':
            cursor.execute("INSERT IGNORE INTO ALUMNO (id_usuario) VALUES (%s)", (id_usuario,))
        elif nuevo_rol == 'profesor':
            cursor.execute("INSERT IGNORE INTO PROFESOR (id_usuario) VALUES (%s)", (id_usuario,))
        elif nuevo_rol == 'administrador':
            cursor.execute("INSERT IGNORE INTO ADMINISTRADOR (id_usuario) VALUES (%s)", (id_usuario,))

        # DETERMINAR A QUIÉN LE PERTENECE ESTE EVENTO
        id_log_dueno = id_admin if id_admin else id_usuario
        mensaje_detalle = f"Modificó el rol de {nombre_completo} a '{nuevo_rol}'"

        query_auditoria = """
            INSERT INTO SESION (id_usuario, status)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                status = %s,
                ultima_conexion = CURRENT_TIMESTAMP \
                          """
        cursor.execute(query_auditoria, (id_log_dueno, mensaje_detalle, mensaje_detalle))

        conn.commit()
        return True

    except Exception as e:
        print("❌ ERROR EN actualizar_rol_usuario:", e)
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def registrar_auditoria_sesion(id_usuario, accion_detalle):
    """Guarda la acción detallada aprovechando el nuevo tamaño VARCHAR(255)."""
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
        print("❌ ERROR EN registrar_auditoria_sesion:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def obtener_logs_auditoria(limite=15):
    """
    Recupera la bitácora unificada definitiva garantizando la visibilidad
    y orden de sesiones, creación de cursos y registros de usuarios.
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
        print("❌ ERROR EN obtener_logs_auditoria TRIPLE COMPLETA:", e)
        return []
    finally:
        cursor.close()
        conn.close()