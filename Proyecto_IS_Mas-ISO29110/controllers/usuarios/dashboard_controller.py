from flask import Blueprint, render_template, session, redirect, url_for
from alchemyClasses.curso import obtener_todos, obtener_por_usuario

from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    """Decorador personalizado para proteger rutas que requieren autenticación."""
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
    """Ruta única que carga el panel de control correspondiente según el rol del usuario."""
    rol = session.get('rol')
    nombre_usuario = session.get('nombre') or session.get('usuario')

    # 1. Panel de Administración
    if rol == 'administrador':
        return render_template(
            'dashboard_admin.html',
            nombre=nombre_usuario,
            rol=rol
        )

    # 2. Panel del Profesor
    if rol == 'profesor':
        id_profesor = session.get('id_usuario')
        # Se obtienen los cursos específicos asignados a este docente
        cursos_docente = obtener_por_usuario(id_profesor, rol)

        return render_template(
            'dashboard_profesor.html',
            nombre=nombre_usuario,
            rol=rol,
            cursos=cursos_docente
        )

    # 3. Panel del Alumno o Usuario general
    # Si no es admin ni profesor, cae aquí automáticamente por defecto
    cursos_totales = obtener_todos()
    return render_template(
        'dashboard_alumno.html',
        nombre=nombre_usuario,
        rol=rol,
        cursos=cursos_totales
    )