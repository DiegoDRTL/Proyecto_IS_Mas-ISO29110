from alchemyClasses.db import get_connection

def get_archivo(id_archivo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CURSO WHERE id_archivo = %s", (id_archivo))
    archivo = cursor.fetchone()
    cursor.close()
    conn.close()
    return archivo

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