from flask import Blueprint, render_template, session, redirect, url_for
from alchemyClasses.curso import obtener_todos, obtener_por_usuario, obtener_disponibles

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
    rol = str(session.get('rol')).strip().lower() # Normalizamos para evitar fallos por mayúsculas
    nombre_usuario = session.get('nombre') or session.get('usuario')
    id_actual = session.get('id_usuario')

    # 1. Panel de Administración
    if rol == 'administrador':
         return render_template(
            'dashboard_admin.html',
            nombre=nombre_usuario,
            rol=rol
        )

    # 2. Panel del Profesor
    if rol == 'profesor':
        # Se obtienen los cursos específicos asignados a este docente
        cursos_docente = obtener_por_usuario(id_actual, rol)

        return render_template(
            'dashboard_profesor.html',
            nombre=nombre_usuario,
            rol=rol,
            cursos=cursos_docente
        )

    # 3. Panel del Alumno o Usuario general
    # Recuperamos los cursos a los que ya se inscribió este alumno en específico
    cursos_inscritos_alumno = obtener_por_usuario(id_actual, 'alumno')

    # Recuperamos el catálogo total de cursos con estado 'Disponible' para que pueda elegir nuevos
    cursos_disponibles_plataforma = obtener_disponibles(id_actual)

    return render_template(
        'dashboard_alumno.html',
        nombre=nombre_usuario,
        rol=rol,
        mis_cursos=cursos_inscritos_alumno,  # Se mapea con el panel 1 del HTML
        cursos=cursos_disponibles_plataforma  # Se mapea con el panel 2 del HTML
    )