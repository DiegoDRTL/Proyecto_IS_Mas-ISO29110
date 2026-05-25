from flask import Blueprint, render_template, session, redirect, url_for
from alchemyClasses.curso import obtener_todos
from alchemyClasses.curso import obtener_por_usuario

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
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
    if session.get('rol') == 'administrador':
        return redirect(url_for('dashboard.admin'))
    return redirect(url_for('dashboard.usuario'))

@dashboard_bp.route('/dashboard/usuario')
@login_required
def usuario():

    rol = session.get('rol')

    # Roles permitidos
    if rol not in ['usuario', 'alumno', 'profesor']:
        return redirect(url_for('dashboard.admin'))

    cursos = obtener_todos()

    return render_template(
        'dashboard_usuario.html',
        nombre=session['usuario'],
        rol=rol,
        cursos=cursos
    )

@dashboard_bp.route('/dashboard/admin')
@login_required
def admin():
    if session.get('rol') != 'administrador':
        return redirect(url_for('dashboard.usuario'))
    return render_template('dashboard_admin.html',
                           nombre=session['usuario'],
                           rol=session['rol'])
