from alchemyClasses.db import get_connection

def get_curso(id_curso):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CURSO WHERE id_curso = %s", (id_curso))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()
    return curso

# Revision
def get_course_by_name(nombre):
    """
    Busca un curso en la base de datos por su nombre exacto.
    Retorna el diccionario del curso si lo encuentra, o None si no existe.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Asumimos que la tabla se llama CURSO en tu base de datos
    cursor.execute("SELECT * FROM CURSO WHERE nombre = %s", (nombre,))
    course = cursor.fetchone()
    cursor.close()
    conn.close()
    return course


def curso_exists(nombre):
    """
    Verifica si el nombre de un curso ya está registrado.
    Utilizado por el controlador antes de procesar el registro.
    """
    return get_course_by_name(nombre) is not None


def create_course(nombre, descripcion, id_profesor):
    """
    Inserta un nuevo curso en la base de datos vinculándolo al profesor.
    Maneja transacciones y aplica rollback en caso de fallas estructurales.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO CURSO (nombre, descripcion, id_profesor) VALUES (%s, %s, %s)",
            (nombre, descripcion, id_profesor)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        # Puedes imprimir el error en consola si necesitas debuggear: print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()