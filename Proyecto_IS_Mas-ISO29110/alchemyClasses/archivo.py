from alchemyClasses.db import get_connection

def get_archivo(id_archivo):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CURSO WHERE id_archivo = %s", (id_archivo))
    archivo = cursor.fetchone()
    cursor.close()
    conn.close()
    return archivo

