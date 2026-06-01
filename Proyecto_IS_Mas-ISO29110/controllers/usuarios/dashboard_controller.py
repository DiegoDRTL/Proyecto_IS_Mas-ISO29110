"""
Módulo de dashboard principal del sistema.

Este controlador gestiona la visualización del panel principal del sistema,
adaptando la información mostrada según el rol del usuario autenticado.

Incluye dashboards diferenciados para administradores, profesores y alumnos,
mostrando métricas, cursos asignados, cursos disponibles y actividades recientes.
"""

from flask import Blueprint, render_template, session, redirect, url_for
from alchemyClasses.curso import obtener_todos, obtener_por_usuario, obtener_disponibles, obtener_metricas_admin
from alchemyClasses.usuario import obtener_usuarios_recientes
from alchemyClasses.archivo import obtener_ultimos_archivos_inscritos
dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    """Protege rutas que requieren autenticación de usuario.

    Este decorador verifica si existe un usuario autenticado en la
    sesión actual. Si no hay sesión activa, redirige al usuario a la
    página de inicio de sesión. En caso contrario, permite la ejecución
    de la función decorada.

    Args:
        f (Callable): Función de vista que será protegida por el
            decorador de autenticación.

    Returns:
        Callable: Función envuelta que valida la sesión antes de
            ejecutar la lógica original.
    """
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated

@dashboard_bp.route('/dashboard')
@login_required
def home():
    """Muestra el panel de control principal según el rol del usuario.

    Esta función determina el rol del usuario autenticado y carga la
    vista correspondiente del dashboard. Dependiendo del rol, muestra
    información específica para administradores, profesores o alumnos,
    incluyendo métricas del sistema, cursos asignados o cursos
    disponibles.

    Returns:
        Response: Plantilla del dashboard correspondiente al rol del
            usuario autenticado, con los datos necesarios para su
            visualización.
    """
    rol = str(session.get('rol')).strip().lower()  # Normalizamos para evitar fallos por mayúsculas
    nombre_usuario = session.get('nombre') or session.get('usuario')
    id_actual = session.get('id_usuario')

    # Panel de Administración
    if rol == 'administrador':

        datos_admin = obtener_metricas_admin()

        # Consulta dinámica de las últimas 4 sesiones de usuarios en la base de datos
        lista_recientes = obtener_usuarios_recientes(limite=4)

        return render_template(

            'dashboard_admin.html',
            nombre=nombre_usuario,
            rol=rol,
            total_usuarios=datos_admin['total_usuarios'],
            total_cursos=datos_admin['total_cursos'],
            cursos_activos=datos_admin['cursos_activos'],
            total_inscripciones=datos_admin['total_inscripciones'],
            total_profesores=datos_admin['total_profesores'],
            usuarios_recientes=lista_recientes
        )

    # Panel del Profesor
    if rol == 'profesor':
        # Se obtienen los cursos específicos asignados a este docente
        cursos_docente = obtener_por_usuario(id_actual, rol)

        return render_template(
            'dashboard_profesor.html',
            nombre=nombre_usuario,
            rol=rol,
            cursos=cursos_docente
        )

    # Panel del Alumno o Usuario general
    # Recuperamos los cursos a los que ya se inscribió este alumno en específico
    cursos_inscritos_alumno = obtener_por_usuario(id_actual, 'alumno')

    inscritos_ids = [curso['id_curso'] for curso in cursos_inscritos_alumno] if cursos_inscritos_alumno else []

    # Recuperamos el catálogo total de cursos con estado 'Disponible' para que pueda elegir nuevos
    cursos_disponibles_plataforma = obtener_disponibles(id_actual)

    # Llamamos a la función de tu archivo 'archivo.py'
    ultimos_archivos_alumno = obtener_ultimos_archivos_inscritos(id_actual, limite=3)

    return render_template(
        'dashboard_alumno.html',
        nombre=nombre_usuario,
        rol=rol,
        mis_cursos=cursos_inscritos_alumno,   # Se mapea con el panel 1 del HTML
        cursos=cursos_disponibles_plataforma, # Se mapea con el panel 2 del HTML
        inscritos_ids=inscritos_ids,
        ultimos_archivos=ultimos_archivos_alumno
    )