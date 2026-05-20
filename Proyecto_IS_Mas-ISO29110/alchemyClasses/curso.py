from alchemyClasses.db import get_connection

def get_curso(id_curso):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CURSO WHERE id_curso = %s", (id_curso))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()
    return curso

def create_curso(id_usuario, estado, nombre, capacidad):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO CURSO (id_usuario, estado, nombre, capacidad) VALUES (%s, %s, %s, %s)",
            (id_usuario, estado, nombre, capacidad)
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