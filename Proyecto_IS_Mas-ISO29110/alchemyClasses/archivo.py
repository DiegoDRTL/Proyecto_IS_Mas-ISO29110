from alchemyClasses.db import get_connection

def get_archivo(id_archivo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ARCHIVO WHERE id_archivo = %s", (id_archivo,))
    archivo = cursor.fetchone()
    cursor.close()
    conn.close()
    return archivo

def obtener_por_curso(id_curso):
    """Se obtienen los archivos de un curso seleccionado"""
    conn = get_connection()
    coursor = conn.cursor(dictionary=True)
    coursor.execute("""
        SELECT a.* FROM ARCHIVO a
        JOIN CURSO_ARCHIVO ca ON a.id_archivo = ca.id_archivo
        WHERE ca.id_curso = %s
    """, (id_curso,))

    archivos = coursor.fetchall()
    conn.close()
    return archivos

def obtener_por_id(id_archivo):
    """Detalles de un archivo seleccionado"""
    conn = get_connection()
    coursor = conn.cursor(dictionary=True)
    coursor.execute("""
        SELECT a.* FROM ARCHIVO a
        WHERE a.id_archivo = %s
    """, (id_archivo,))
    archivo = coursor.fetchone()
    conn.close()
    return archivo

def verifica_pertenece_curso(id_archivo, id_curso):
    """Verifica pertenencia de un archivo en un curso"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM CURSO_ARCHIVO
        WHERE id_archivo = %s AND id_curso = %s
    """, (id_archivo, id_curso))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None


def delete_archivo_db(id_archivo):
    """
    Realiza la baja o borrado físico del registro del archivo en la base de datos.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ARCHIVO WHERE id_archivo = %s", (id_archivo,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def create_archivo(nombre, tipo_extension, fecha_subida, ruta, id_curso):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO ARCHIVO (nombre, tipo_extension, fecha_subida, ruta) VALUES (%s, %s, %s)",
            (nombre, tipo_extension, fecha_subida, ruta)
        )
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        id = cursor.fetchone
        cursor.execute(
            "IINSERT INTO CURSO_ARCHIVO (id_curso, id_archivo) VALUES (%s, %s)",
            (id_curso, id)
        )
        conn.commit()
        return id
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_archivo_by_name(nombre):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM ARCHIVO WHERE nombre = %s",
        (nombre,)
    )

    archivo = cursor.fetchone()

    cursor.close()
    conn.close()

    return archivo


def archivo_exists(nombre):
    return get_archivo_by_name(nombre) is not None