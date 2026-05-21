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

    cursor.execute(
        """
        SELECT * FROM INSCRIBE
        WHERE id_usuario = %s AND id_curso = %s
        """,
        (id_usuario, id_curso)
    )

    inscripcion = cursor.fetchone()

    cursor.close()
    conn.close()

    return inscripcion is not None


def curso_disponible(id_curso):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT capacidad
        FROM CURSO
        WHERE id_curso = %s
        """,
        (id_curso,)
    )

    curso = cursor.fetchone()

    if not curso:
        cursor.close()
        conn.close()
        return False

    capacidad = curso['capacidad']

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM INSCRIBE
        WHERE id_curso = %s
        """,
        (id_curso,)
    )

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
        cursor.execute(
            """
            INSERT INTO INSCRIBE (id_usuario, id_curso)
            VALUES (%s, %s)
            """,
            (id_usuario, id_curso)
        )

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