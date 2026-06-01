"""
Módulo de reportes de cursos.

Este controlador genera la vista de reportes administrativos de cursos,
mostrando información consolidada del sistema. Está diseñado para usuarios
autenticados con permisos adecuados.

Recupera datos desde la capa de servicios para mostrar estadísticas o
listados de cursos registrados.
"""

from flask import Blueprint, render_template, session, redirect, url_for
from alchemyClasses.curso import obtener_reporte_cursos

reportes_cursos_bp = Blueprint(
    'reportes_cursos',
    __name__
)

@reportes_cursos_bp.route('/admin/reportes-cursos')
def visualizar_reportes():
    """Muestra el reporte general de cursos registrados en el sistema.

    Verifica que exista una sesión activa, obtiene la información
    necesaria para generar el reporte de cursos y renderiza la plantilla
    correspondiente para su visualización.

    Returns:
        Response: Redirección al inicio de sesión cuando no existe una
            sesión activa, o plantilla renderizada con el reporte de
            cursos disponibles.
    """
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    cursos = obtener_reporte_cursos()

    return render_template(
        'reportes_cursos_admin.html',
        cursos=cursos
    )