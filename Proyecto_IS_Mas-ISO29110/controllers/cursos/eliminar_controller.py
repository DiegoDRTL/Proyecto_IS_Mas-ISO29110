from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.curso import deleate_curso

# Definición del blueprint
eliminar_curso_bp = Blueprint('eliminar_curso', __name__)

@eliminar_curso_bp.route('/cursos/<int:id_curso>/eliminar')
def eliminar_curso(id_curso):
    # CORRECION 'user_id' por 'id_usuario'
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    rol = session.get('rol')

    if rol == 'profesor':

        exito = deleate_curso(id_curso)

        if exito:
            flash('Curso eliminado correctamente', 'realizado')
        else:
            flash('No se pudo eliminar el curso, intente nuevamente', 'error')

        return redirect(url_for('dashboard.home'))

    else:
        flash('No tienes acceso a esta opción', 'error')
        # CORRECCION del return
        return redirect(url_for('dashboard.home'))