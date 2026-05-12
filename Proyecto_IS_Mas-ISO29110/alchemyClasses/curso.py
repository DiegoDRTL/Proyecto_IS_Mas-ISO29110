from alchemyClasses.db import get_connection

def get_curso(id_curso):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CURSO WHERE id_curso = %s", (id_curso))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()
    return curso

