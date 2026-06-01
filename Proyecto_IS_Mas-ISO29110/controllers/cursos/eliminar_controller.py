"""
Módulo de eliminación de cursos.

Este controlador gestiona la eliminación de cursos dentro del sistema,
validando que el usuario tenga sesión activa antes de permitir la operación.
Solo usuarios con permisos adecuados pueden eliminar cursos del sistema.

Incluye lógica de validación de sesión, eliminación de registros y manejo
de mensajes de éxito o error.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.curso import deleate_curso

# Definición del blueprint
eliminar_curso_bp = Blueprint('eliminar_curso', __name__)

@eliminar_curso_bp.route('/cursos/<int:id_curso>/eliminar')
def eliminar_curso(id_curso):
    """Elimina un curso existente del sistema.

    Verifica que el usuario tenga una sesión activa y que posea el rol
    de profesor. Si cumple con los permisos requeridos, ejecuta la
    operación de eliminación del curso indicado y notifica el resultado
    mediante mensajes flash. Finalmente, redirige al panel principal.

    Args:
        id_curso (int): Identificador único del curso que se desea
            eliminar.

    Returns:
        Response: Redirección al inicio de sesión cuando no existe una
            sesión activa, o al panel principal después de procesar la
            solicitud de eliminación.
    """
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