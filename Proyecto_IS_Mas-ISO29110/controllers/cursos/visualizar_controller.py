from flask import Blueprint, render_template, redirect, url_for, session
from alchemyClasses import curso

visualizarCurso_bp = Blueprint('course', __name__)

@visualizarCurso_bp.route('/cursos')
def visualizar_cursos():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    rol =session.get('rol')
    id_usuario = session.get('user.id')

    if rol == 'Administrador':
        cursos = curso.obtener_todos()
    else:
        cursos = curso.obtener_por_usuario(id_usuario, rol)

    return render_template('cursos.html', cursos=cursos, rol=rol)

