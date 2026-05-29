from flask import Blueprint, render_template, session, redirect, url_for
from alchemyClasses.curso import obtener_reporte_cursos

reportes_cursos_bp = Blueprint(
    'reportes_cursos',
    __name__
)

@reportes_cursos_bp.route('/admin/reportes-cursos')
def visualizar_reportes():

    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    cursos = obtener_reporte_cursos()

    return render_template(
        'reportes_cursos_admin.html',
        cursos=cursos
    )