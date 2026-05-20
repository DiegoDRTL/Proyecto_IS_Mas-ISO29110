from alchemyClasses.db import get_connection

def get_archivo(id_archivo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ARCHIVO WHERE id_archivo = %s", (id_archivo))
    archivo = cursor.fetchone()
    cursor.close()
    conn.close()
    return archivo

def create_archivo(nombre, tipo_extension, fecha_subida):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO ARCHIVO (nombre, tipo_extension, fecha_subida) VALUES (%s, %s, %s)",
            (nombre, tipo_extension, fecha_subida)
        )
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        id = cursor.fetchone
        return id
    except Exception as e:
        conn.rollback()
        return -1
    finally:
        cursor.close()
        conn.close()

def deleate_archivo(id_archivo):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM ARCHIVO WHERE id_archivo='%s'",
            (id_archivo)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()