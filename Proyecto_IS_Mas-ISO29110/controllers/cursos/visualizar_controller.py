"""
Módulo de visualización de cursos.

Este controlador permite visualizar los cursos disponibles en el sistema
según el rol del usuario autenticado. Los administradores pueden ver todos
los cursos, mientras que los usuarios regulares solo ven aquellos asociados
a su cuenta.

Incluye lógica de filtrado de cursos y renderizado del dashboard correspondiente.
"""

from flask import Blueprint, render_template, redirect, url_for, session
from alchemyClasses import curso


visualizarCurso_bp = Blueprint('visualizar_curso', __name__)

@visualizarCurso_bp.route('/cursos')
def visualizar_cursos():
    """Muestra la lista de cursos disponibles para el usuario.

    Verifica que exista una sesión activa y obtiene los cursos que deben
    mostrarse según el rol del usuario autenticado. Los administradores
    pueden visualizar todos los cursos registrados, mientras que los
    demás usuarios únicamente visualizan los cursos asociados a su perfil.

    Returns:
        Response: Redirección al inicio de sesión cuando no existe una
            sesión activa, o plantilla renderizada con la lista de cursos
            correspondiente al usuario.
    """
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    rol =session.get('rol')
    id_usuario = session.get('id_usuario')

    if rol == 'Administrador':
        cursos = curso.obtener_todos()
    else:
        cursos = curso.obtener_por_usuario(id_usuario, rol)

    return render_template('cursos.html', cursos=cursos, rol=rol)
