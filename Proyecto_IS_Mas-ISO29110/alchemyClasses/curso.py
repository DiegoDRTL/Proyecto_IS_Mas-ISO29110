from alchemyClasses.db import get_connection


class Curso:

    def obtener_todos(self):
        """Caso especial para Admin"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*,
                   u.nombre, u.apellido_paterno, u.apellido_materno
            FROM Curso c
            JOIN USUARIO u ON c.id_usuario = u.id_usuario""")
        cursos = cursor.fetchall()
        conn.close()
        return cursos

    def obtener_por_usuario(id_usuario, rol):
        """Cursos que se muestran según rol """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if rol == 'Profesor':
            cursor.execute("""
                SELECT c.* u.nombre, u.apellido_paterno, u.apellido_materno
                FROM Curso c
                JOIN USUARIO u ON c.id_usuario = u.id_usuario
                WHERE c.id_usuario= %s
            """, (id_usuario,))

        elif rol == 'Alumno':
            cursor.execute("""
                SELECT c.* u.nombre, u.apellido_paterno, u.apellido_materno
                FROM Curso c
                JOIN INSCRIBE i ON c.id_curso = i.id_curso
                JOIN USUARIO u ON c.id_usuario = u.id_usuario
                WHERE i.id_usuario = %s
            """, (id_usuario,))
        cursos = cursor.fetchall()
        conn.close()
        return cursos


    def obtener_por_id(id_curso):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.* u.nombre, u.apellido_paterno, u.apellido_materno
            FROM Curso c
            JOIN USUARIO u ON c.id_usuario = u.id_usuario
            WHERE c.id_usuario= %s
        """, (id_curso,))
        curso = cursor.fetchone()
        conn.close()
        return curso

    def obtener_disponibles(self):
        """Cursos que se pueden inscribir"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.* u.nombre , u.apellido_paterno, u.apellido_materno
            FROM CURSO c
            JOIN USUARIO u ON c.id_usuario = u.id_usuario
            WHERE c.estado = 'Disponible
            '""")
        curso = cursor.fetchone()
        conn.close()
        return curso

    def obtener_archivos(id_curso):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.* 
            FROM ARCHIVO a 
            JOIN CURSO_ARCHIVO ca ON a.id_archivo = ca.id_archivo
            WHERE ca.id_curso = %s
        """, (id_curso,))
        archivos = cursor.fetchall()
        conn.close()
        return archivos

