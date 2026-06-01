"""
Módulo de gestión de profesores.

Este controlador permite a los administradores visualizar y administrar
la lista de profesores del sistema, así como eliminar registros cuando
sea necesario.

Incluye validación de permisos y operaciones sobre usuarios con rol de
profesor.
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from alchemyClasses.usuario import obtener_profesor, eliminar_usuario

profesor_bp = Blueprint('profesor', __name__)

@profesor_bp.route('/profesores')
def gestionar_profesores():
    """Muestra la lista de profesores registrados en el sistema.

    Verifica que el usuario tenga una sesión activa y que posea el rol
    de administrador. Si cumple con los permisos, obtiene la lista de
    profesores desde la base de datos y la envía a la plantilla para su
    visualización. En caso contrario, se muestra un mensaje de acceso
    no autorizado.

    Returns:
        Response: Plantilla con la lista de profesores cuando el usuario
            es administrador, o redirección al login en caso contrario.
    """
    if 'id_usuario' not in session or session.get('rol') != 'administrador':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('auth.login'))

    profesores = obtener_profesor()
    return render_template('profesores.html', profesores=profesores)

@profesor_bp.route('/profesores/<int:id_usuario>/eliminar', methods=['POST'])
def eliminar_profesor(id_usuario):
    """Elimina un profesor del sistema.

    Verifica que el usuario autenticado tenga el rol de administrador.
    Si la validación es correcta, procede a eliminar el usuario
    correspondiente (profesor) del sistema. Finalmente, informa el
    resultado de la operación mediante mensajes flash.

    Args:
        id_usuario (int): Identificador del profesor que se desea eliminar.

    Returns:
        Response: Redirección a la vista de gestión de profesores cuando
            la operación finaliza, o redirección al login si no hay
            permisos suficientes.
    """
    if 'id_usuario' not in session or session.get('rol') != 'administrador':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('auth.login'))

    exito = eliminar_usuario(id_usuario)

    if exito:
        flash('Profesor eliminado correctamente', 'realizado')
    else:
        flash('No se pudo eliminar el profesor, intente nuevamente', 'error')

    return redirect(url_for('profesor.gestionar_profesores'))
