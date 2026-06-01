from alchemyClasses.db import get_connection

def get_curso_by_id(id_curso):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM CURSO WHERE id_curso = %s",
        (id_curso,)
    )

    curso = cursor.fetchone()

    cursor.close()
    conn.close()

    return curso


def get_curso_by_name(nombre):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM CURSO WHERE nombre = %s",
        (nombre,)
    )

    curso = cursor.fetchone()

    cursor.close()
    conn.close()

    return curso


def curso_exists(nombre):
    return get_curso_by_name(nombre) is not None

def create_course(nombre, capacidad, estado, descripcion, id_usuario):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO CURSO
                (id_usuario, estado, nombre, capacidad, descripcion)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (id_usuario, estado, nombre, capacidad, descripcion)
        )

        id_generado = cursor.lastrowid

        # INSERTAR O ACTUALIZAR LA BITÁCORA EN LA TABLA SESION
        # Creamos la cadena con la acción realizada por el profesor
        mensaje_accion = f"Creó un nuevo curso de idiomas titulado '{nombre}'"

        # insertará la acción, o si el usuario ya existe, actualizará su fila reemplazando el estado viejo con la creación del curso
        query_auditoria = """
            INSERT INTO SESION (id_usuario, status)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                status = %s,
                ultima_conexion = CURRENT_TIMESTAMP() \
                          """
        cursor.execute(query_auditoria, (id_usuario, mensaje_accion, mensaje_accion))

        conn.commit()

        return id_generado if id_generado else True

    except Exception as e:
        conn.rollback()
        print("❌ ERROR EN BASE DE DATOS (create_course):", e)
        return None

    finally:
        cursor.close()
        conn.close()

def obtener_todos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.*,
               u.nombre,
               u.apellido_paterno,
               u.apellido_materno
        FROM CURSO c
        JOIN USUARIO u
        ON c.id_usuario = u.id_usuario
    """)

    cursos = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return cursos


def obtener_por_usuario(id_usuario, rol):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    rol_normalizado = str(rol).strip().lower()

    if rol_normalizado == 'profesor':
        cursor.execute("""
            SELECT c.id_curso,
                   c.nombre AS curso_nombre,
                   c.estado,
                   c.capacidad,
                   c.descripcion,
                   COUNT(i.id_usuario) AS total_inscritos,
                   u.nombre,
                   u.apellido_paterno,
                   u.apellido_materno
            FROM CURSO c
            JOIN USUARIO u ON c.id_usuario = u.id_usuario
            LEFT JOIN INSCRIBE i ON c.id_curso = i.id_curso
            WHERE c.id_usuario = %s AND c.estado != 'Eliminado'  
            GROUP BY c.id_curso
                       """, (id_usuario,))

    elif rol_normalizado == 'alumno':
        cursor.execute("""
            SELECT c.id_curso,
                c.nombre AS curso_nombre,
                c.descripcion,
                c.estado, 
                c.capacidad,
                u.nombre AS profe_nombre,
                u.apellido_paterno,
                u.apellido_materno
            FROM CURSO c
            JOIN INSCRIBE i ON c.id_curso = i.id_curso
            JOIN USUARIO u ON c.id_usuario = u.id_usuario
            WHERE i.id_usuario = %s
        """, (id_usuario,))

    else:
        cursos = []
        cursor.close()
        conn.close()
        return cursos

    cursos = cursor.fetchall()
    cursor.close()
    conn.close()
    return cursos

def obtener_por_id(id_curso):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.id_curso,
               c.nombre,
               c.estado,
               c.capacidad,
               c.descripcion,
               c.id_usuario,
               u.nombre AS profesor_nombre,
               u.apellido_paterno,
               u.apellido_materno
        FROM CURSO c
        JOIN USUARIO u
        ON c.id_usuario = u.id_usuario
        WHERE c.id_curso = %s
    """, (id_curso,))

    curso = cursor.fetchone()

    cursor.close()
    conn.close()

    return curso


def obtener_disponibles(id_alumno):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            c.id_curso,
            c.nombre AS curso_nombre,
            c.descripcion,
            c.estado,
            c.capacidad,

            COUNT(i.id_usuario) AS total_inscritos,

            u.nombre AS profe_nombre,
            u.apellido_paterno,
            u.apellido_materno

        FROM CURSO c

        JOIN USUARIO u 
            ON c.id_usuario = u.id_usuario

        LEFT JOIN INSCRIBE i
            ON c.id_curso = i.id_curso

        WHERE (c.estado = 'Disponible' OR c.estado = 'Abierto')

        AND c.id_curso NOT IN (
            SELECT id_curso
            FROM INSCRIBE
            WHERE id_usuario = %s
        )

        GROUP BY c.id_curso
    """

    cursor.execute(query, (id_alumno,))
    cursos = cursor.fetchall()

    cursor.close()
    conn.close()

    return cursos

def obtener_archivos(id_curso):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.*
        FROM ARCHIVO a
        JOIN CURSO_ARCHIVO ca
        ON a.id_archivo = ca.id_archivo
        WHERE ca.id_curso = %s
    """, (id_curso,))

    archivos = cursor.fetchall()

    cursor.close()
    conn.close()

    return archivos


def alumno_existe(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM ALUMNO WHERE id_usuario = %s",
        (id_usuario,)
    )

    alumno = cursor.fetchone()

    cursor.close()
    conn.close()

    return alumno is not None


def alumno_inscrito(id_usuario, id_curso):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM INSCRIBE
        WHERE id_usuario = %s
        AND id_curso = %s
    """, (id_usuario, id_curso))

    inscripcion = cursor.fetchone()

    cursor.close()
    conn.close()

    return inscripcion is not None


def curso_disponible(id_curso):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT capacidad
        FROM CURSO
        WHERE id_curso = %s
    """, (id_curso,))

    curso = cursor.fetchone()

    if not curso:
        cursor.close()
        conn.close()
        return False

    capacidad = curso['capacidad']

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM INSCRIBE
        WHERE id_curso = %s
    """, (id_curso,))

    total = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    return total < capacidad


def inscribir_alumno(id_usuario, identificador_curso):

    if not alumno_existe(id_usuario):
        print("El alumno no existe")
        return False

    if isinstance(identificador_curso, int):
        curso = get_curso_by_id(identificador_curso)
    else:
        curso = get_curso_by_name(identificador_curso)

    if not curso:
        print("El curso no existe")
        return False

    id_curso = curso['id_curso']

    if alumno_inscrito(id_usuario, id_curso):
        print("El alumno ya está inscrito")
        return False

    if not curso_disponible(id_curso):
        print("El curso ya no tiene cupo")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO INSCRIBE (id_usuario, id_curso)
            VALUES (%s, %s)
        """, (id_usuario, id_curso))

        conn.commit()

        print("Inscripción realizada correctamente")
        return True

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        return False

    finally:
        cursor.close()
        conn.close()

def deleate_curso(id_curso):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Eliminamos primero los registros de las tablas hijas para evitar conflictos de integridad
        cursor.execute("DELETE FROM INSCRIBE WHERE id_curso = %s", (id_curso,))
        cursor.execute("DELETE FROM CURSO_ARCHIVO WHERE id_curso = %s", (id_curso,))

        # borramos el curso de la tabla principal de forma segura
        cursor.execute("DELETE FROM CURSO WHERE id_curso = %s", (id_curso,))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("ERROR AL ELIMINAR EL CURSO Y SUS RELACIONES:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def obtener_metricas_admin():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    metricas = {
        'total_usuarios': 0,
        'total_cursos': 0,
        'cursos_activos': 0,
        'total_inscripciones': 0,
        'total_profesores': 0,
    }

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM USUARIO")
        metricas['total_usuarios'] = cursor.fetchone()['total']
    except Exception as e:
        print("Error al contar usuarios:", e)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM CURSO")
        metricas['total_cursos'] = cursor.fetchone()['total']
    except Exception as e:
        print("Error al contar cursos:", e)

    try:
        cursor.execute("""
                       SELECT COUNT(*) AS total
                       FROM CURSO
                       WHERE estado IN ('Disponible', 'Abierto', 'Activo')
                       """)
        metricas['cursos_activos'] = cursor.fetchone()['total']
    except Exception as e:
        print("Error al contar cursos activos:", e)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM INSCRIBE")
        metricas['total_inscripciones'] = cursor.fetchone()['total']
    except Exception as e:
        print("Error al contar inscripciones:", e)

    # NUEVA CONSULTA: Contar cuántos usuarios tienen asignado el rol de profesor
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM USUARIO WHERE LOWER(rol) = 'profesor'")
        metricas['total_profesores'] = cursor.fetchone()['total']
    except Exception as e:
        print("Error al contar profesores:", e)

    cursor.close()
    conn.close()
    return metricas

def dar_baja_curso(id_usuario, id_curso):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # eliminar inscripción
        cursor.execute("""
            DELETE FROM INSCRIBE
            WHERE id_usuario = %s
            AND id_curso = %s
        """, (id_usuario, id_curso))

        # devolver cupo al curso
        cursor.execute("""
            UPDATE CURSO
            SET capacidad = capacidad + 1
            WHERE id_curso = %s
        """, (id_curso,))

        conn.commit()

        print("Baja realizada correctamente")
        return True

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        return False

    finally:
        cursor.close()
        conn.close()

def update_course_status(id_curso, nuevo_estado):
    """Cambia el estado de un curso (ej. de 'Abierto' a 'Cerrado' o viceversa)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE CURSO
            SET estado = %s
            WHERE id_curso = %s
            """,
            (nuevo_estado, id_curso)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("ERROR EN BASE DE DATOS AL ACTUALIZAR ESTADO:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def update_course_data(id_curso, nombre, capacidad, descripcion):
    """Actualiza los detalles de un curso en fase de borrador"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE CURSO
            SET nombre = %s, capacidad = %s, descripcion = %s
            WHERE id_curso = %s
            """,
            (nombre, capacidad, descripcion, id_curso)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("ERROR AL ACTUALIZAR DATOS DEL CURSO:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def obtener_reporte_cursos():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.id_curso,
            c.nombre AS curso_nombre,
            c.estado,
            c.capacidad,

            COUNT(i.id_usuario) AS total_inscritos,

            u.nombre AS profesor_nombre,
            u.apellido_paterno,
            u.apellido_materno

        FROM CURSO c

        JOIN USUARIO u
            ON c.id_usuario = u.id_usuario

        LEFT JOIN INSCRIBE i
            ON c.id_curso = i.id_curso

        GROUP BY c.id_curso
    """)

    cursos = cursor.fetchall()

    cursor.close()
    conn.close()

    return cursos