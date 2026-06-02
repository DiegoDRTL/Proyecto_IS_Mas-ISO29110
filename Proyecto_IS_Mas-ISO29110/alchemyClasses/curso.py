"""
Modelos de cursos

Este modelo incluye todas las funciones que mandan a llamar los controladore de curso
"""
from alchemyClasses.db import get_connection

def get_curso_by_id(id_curso):
    """
    Obtiene toda la informacion del curso con el id ingresado

    Args:
        id_curso (int): Clave primaria del curso del cual se obtendra la informacion.

    Returns:
        Response: La informacion del curso en formato de diccionario.
    """
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
    """
    Obtiene toda la informacion de un curso usando su nombre

    Args:
        nombre (str): Nombre del curso del cual se obtendra la informacion.

    Returns:
        Response: La informacion del curso en formato de diccionario.
    """
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
    """
    Comprueba si ya existe en la BD un curso con el mismo nombre ingresado

    Returns:
        Response: True en caso de existir un curso con el mismo nombre en la BD.
    """
    return get_curso_by_name(nombre) is not None

def create_course(nombre, capacidad, estado, descripcion, id_usuario):
    """
    Con la informacion ingresada se registra un nuevo curso en la BD
    Devuelve el ID del curso en caso de exito

    Args:
        nombre (str): Nombre con el que se va a registrar el curso en la BD.
        capacidad (int): Capacidad maxima que impuso el profesor para su curso
        estado (str): Estado actual del curso (Abierto o Cerrado)
        descripcion (str): Descripcion del curso proporcionada por el profesor
        id_usuario (int): Clave primaria del profesor que crea el curso

    Returns:
        Response: True en caso de registrar con exito el curso en la BD, False en caso contrario.
    """
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
    """
    Obtiene la informacion de todos los cursos en el sistema

    Returns:
        Response: La informacion de los cursos en formato de diccionario.
    """
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
    """
    Regresa la informacion de los cursos segun el usuario que lo solicite

    Args:
        id_usuario (int): Clave primaria del usuario del cual se obtendra sus cursos.
        rol (str): Cadena de texto con el rol del usuario.

    Returns:
        Response: En caso de ser alumnos: regresa los cursos a los que esta inscrito
                  En caso de ser profesor: regresa los cursos que imparte
    """
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
    """
    Obtiene toda la informacion del curso con el id ingresado

    Args:
        id_curso (int): Clave primaria del curso del cual se obtendra la informacion.

    Returns:
        Response: La informacion del curso en formato de diccionario.
    """
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
    """
    Regresa los cursos que todavia tienen cupo y no los tenga registrados el alumno con el ID ingresado

    Args:
        id_alumno (int): Clave primaria del alumno para obtener los cursos a los que se puede inscribir.

    Returns:
        Response: La informacion de los curso en formato de diccionario.
    """

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
    """
    Regresa una lista con los archivos que se encuentran en el curso

    Args:
        id_curso (int): Clave primaria del curso del cual se obtendra sus archivos.

    Returns:
        Response: La informacion de los archivos del curso en formato de diccionario.
    """
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
    """
    Comprueba si el alumno del id ingresado se encuentra en el sistema

    Args:
        id_usuario (int): Clave primaria del usuario a verificar si existe.

    Returns:
        Response: True en caso de que exista el usuario en el sistema, False en caso contrario.
    """
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
    """
    Comprueba si el alumno con id ingresado ya se encuentra en el curso con id ingresado

    Args:
        id_usuario (int): Clave primaria del usuario a verificar si se encuentra en el curso.
        id_curso (int): Clave primaria del curso a verificar.

    Returns:
        Response: True en caso de que el usuario se encuentre en el curso, False en caso contrario.
    """
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
    """
    Conprueba si la capacidad actual del curso es menor al su limite

    Args:
        id_curso (int): Clave primaria del curso a verificar si aun tiene cupo.

    Returns:
        Response: True en caso de que aun tenga cupo el curso, False en caso contrario.
    """
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
    """
    Inscribe al alumno con el id dado en el curso que solicito

    Args:
        id_usuario (int): Clave primaria del usuario que se va a inscribor en el curso.
        identificador_curso (int): Clave primaria del curso al que se va a registrar el usuario.

    Returns:
        Response: True si la inscripcion al curso es exitoso, False en cualquier otro caso.
    """

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
    """
    Elimina toda la informacion de la BD del curso del ID dado

    Args:
        id_curso (int): Clave primaria del curso a eliminar de la BD.

    Returns:
        Response: True en caso de haber eliminado con exito el curso, False en cualquier otro caso.
    """
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
    """
    Obtiene un conteo con informacion importante para el administrador
    Devuelve la cantidad de usuarios, cursos (activos e inactivos)
    inscripciones realizadas y profesores del sistema

    Returns:
        Response: Diccionario con los datos del sistema.
    """
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
    """
    Funcion que dado un usuario se elimina su inscripcion del curso correspondiente

    Args:
        id_usuario (int): Clave primaria del usario que se va a dar de baja.
        id_curso (int): Clave primaria del curso del que se va a dar de baja el usuario.

    Returns:
        Response: True si se elimino la inscripcion del usuario, False en caso contrario.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM INSCRIBE
            WHERE id_usuario = %s
            AND id_curso = %s
        """, (id_usuario, id_curso))

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
    """
    Cambia el estado de un curso (ej. de 'Abierto' a 'Cerrado' o viceversa)
    
    Args:
        id_curso (int): Clave primaria del curso al que se le cambiara su estado.
        nuevo_estado (str): Estado al que sera cambiado el curso

    Returns:
        Response: True en caso de que el cambio de estado sea exitoso, False en caso contrario.
    """
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
    """
    Actualiza los detalles de un curso en fase de borrador

    Args:
        id_curso (int): Clave primaria del curso al que se le van a hacer modificaciones
        nombre (str): Nombre con el que se va a actualizar el curso en la BD.
        capacidad (int): Capacidad maxima actualizada que impuso el profesor para su curso
        descripcion (str): Descripcion actualizada del curso proporcionada por el profesor

    Returns:
        Response: True en caso de que la actualizacion del curso sea exitosa en la BD
                  False en caso contrario.
    """
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
    """
    Obtiene los registros con valores actuales de los cursos dentro sistema

    Returns:
        Response: La informacion de los curso del sistema en formato de diccionario.
    """

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