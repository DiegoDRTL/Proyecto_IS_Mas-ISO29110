"""
Modelos de archivos

Este modelo incluye todas las funciones que mandan a llamar los controladores de archivo
"""
from alchemyClasses.db import get_connection

def get_archivo(id_archivo):
    """
    Obtiene la informacion del archivo con el ID insertado

    Args:
        id_archivo (int): Clave primaria del archivo del cual se obtendra la informacion.

    Returns:
        Response: La informacion del archivo en formato de diccionario.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ARCHIVO WHERE id_archivo = %s", (id_archivo,))
    archivo = cursor.fetchone()
    cursor.close()
    conn.close()
    return archivo

def obtener_por_curso(id_curso):
    """
    Se obtienen los archivos de un curso seleccionado
    
    Args:
        id_curso (int): Clave primaria del curso del cual se obtendra sus archivos.

    Returns:
        Response: La informacion de los archivos del curso en formato de diccionario.
    """
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
    """
    Detalles de un archivo seleccionado
    
    Args:
        id_archivo (int): Clave primaria del archivo del cual se obtendra la informacion.

    Returns:
        Response: La informacion del archivo en formato de diccionario.
    """
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
    """
    Verifica pertenencia de un archivo en un curso
    
    Args:
        id_archivo (int): Clave primaria del archivo a verificar si se encuentra en el curso.
        id_curso (int): Clave primaria del curso a verificar.

    Returns:
        Response: True en caso de que exista el archivo en el curso, False en caso contrario.
    """
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

    Args:
        id_archivo (int): Clave primaria del archivo que se va a eliminar de la BD.

    Returns:
        Response: True en caso de que se haya eliminado con exito el archivo de la BD
                  False en caso contrario.
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
    """
    Con la informacion insertada se registra un nuevo archivo en la BD
    
    Args:
        nombre (str): Nombre con el que queda registrado el archivo en la BD
        tipo_extension (str): Tipo de extension del archivo a subir
        fecha_subida (date): fecha actual en la que se registro el archivo en formato MM/DD/AAAA
        ruta (str): direccion fisica en la que se encuentra alojado el archivo
        id_curso (int): Clave primaria del curso donde se sube el archivo

    Returns:
        Response: En caso de que el registro sea exitoso regresa el ID con el que se registro en la BD,
                  False en caso contrario.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO ARCHIVO
            (nombre, tipo_extension, fecha_subida, ruta)
            VALUES (%s, %s, %s, %s)
            """,
            (nombre, tipo_extension, fecha_subida, ruta)
        )

        id_archivo = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO CURSO_ARCHIVO
            (id_curso, id_archivo)
            VALUES (%s, %s)
            """,
            (id_curso, id_archivo)
        )
 
        conn.commit()
        return id_archivo

    except Exception as e:
        conn.rollback()
        print("ERROR EN create_archivo:", e)
        return False

    finally:
        cursor.close()
        conn.close()

def get_archivo_by_name(nombre):
    """
    Regresa la informacion de un archivo por su nombre

    Args:
        nombre (str): Nombre del archivo del cual se obtendra la informacion.

    Returns:
        Response: La informacion del archivo en formato de diccionario.
    """
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
    """
    Comprueba si ya existe en la BD un archivo con el mismo nombre insertado

    Args:
        nombre (str): Nombre del archivo a verificar.

    Returns:
        Response: True en caso de existir un archivo con el mismo nombre en la BD, False en caso contrario.
    """
    return get_archivo_by_name(nombre) is not None


def obtener_archivos(id_curso, id_usuario):
    """
    Obtiene los archivos de un curso únicamente si el usuario está inscrito en él.
    
    Args:
        id_curso (int): Clave primaria del curso del que se van a obtener los archivos.
        id_usuario (int): Clave primaria del usuario inscrito en el curso.

    Returns:
        Response: La informacion de los archivos en el curso en formato de diccionario.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.*
        FROM ARCHIVO a
        JOIN CURSO_ARCHIVO ca ON a.id_archivo = ca.id_archivo
        JOIN INSCRIBE i ON ca.id_curso = i.id_curso
        WHERE ca.id_curso = %s AND i.id_usuario = %s
    """, (id_curso, id_usuario))

    archivos = cursor.fetchall()
    cursor.close()
    conn.close()
    return archivos


def obtener_ultimos_archivos_inscritos(id_usuario, limite=4):
    """
    Obtiene los últimos archivos subidos globalmente, filtrando solo
    aquellos de los cursos donde el alumno se encuentra inscrito.
    
    Args:
        id_usuario (int): Clave primaria del usuario del que se obtendran los ultimos
                          4 archivos que se subieron a los cursos a los que esta inscrito.
        limite (int): Numero limite de archivos que se obtendran en la respuesta

    Returns:
        Response: La informacion de los ultimos 4 archivos subidos en los cursos inscritos.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.*, c.nombre AS curso_nombre, ca.id_curso
        FROM ARCHIVO a
        JOIN CURSO_ARCHIVO ca ON a.id_archivo = ca.id_archivo
        JOIN CURSO c ON ca.id_curso = c.id_curso
        JOIN INSCRIBE i ON c.id_curso = i.id_curso
        WHERE i.id_usuario = %s
        ORDER BY a.fecha_subida DESC
        LIMIT %s
    """, (id_usuario, limite))

    archivos = cursor.fetchall()
    cursor.close()
    conn.close()
    return archivos