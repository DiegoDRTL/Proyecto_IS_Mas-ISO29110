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


def create_course(id_curso, id_profesor, estado, nombre, capacidad):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO CURSO
            (id_curso, id_usuario, estado, nombre, capacidad)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (id_curso, id_profesor, estado, nombre, capacidad)
        )

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        return False

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

    if rol == 'Profesor':
        cursor.execute("""
            SELECT c.*,
                   u.nombre,
                   u.apellido_paterno,
                   u.apellido_materno
            FROM CURSO c
            JOIN USUARIO u
            ON c.id_usuario = u.id_usuario
            WHERE c.id_usuario = %s
        """, (id_usuario,))

    elif rol == 'Alumno':
        cursor.execute("""
            SELECT c.*,
                   u.nombre,
                   u.apellido_paterno,
                   u.apellido_materno
            FROM CURSO c
            JOIN INSCRIBE i
            ON c.id_curso = i.id_curso
            JOIN USUARIO u
            ON c.id_usuario = u.id_usuario
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
        SELECT c.*,
               u.nombre,
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


def obtener_disponibles():
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
        WHERE c.estado = 'Disponible'
    """)

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
        cursor.execute(
            "DELETE FROM CURSO WHERE id_curso='%s'",
            (id_curso)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
