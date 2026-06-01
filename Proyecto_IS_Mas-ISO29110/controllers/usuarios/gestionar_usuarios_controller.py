"""
Módulo de gestión de usuarios.

Este controlador permite a los administradores visualizar, actualizar roles
y eliminar usuarios dentro del sistema. Incluye operaciones de administración
sobre la base de datos de usuarios registrados.

También maneja la actualización de roles y la eliminación de usuarios con
control de permisos.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from alchemyClasses.usuario import (
    obtener_todos_usuarios,
    actualizar_rol_usuario,
    eliminar_usuario
)

gestionar_usuarios_bp = Blueprint(
    'gestionar_usuarios',
    __name__
)

@gestionar_usuarios_bp.route('/gestionar_usuarios')
def gestionar_usuarios():
    """Muestra la vista de administración de usuarios.

    Obtiene la lista completa de usuarios registrados en el sistema y la
    envía a la plantilla de gestión para su visualización y
    administración por parte del usuario correspondiente.

    Returns:
        Response: Plantilla de administración de usuarios con la lista
            completa de usuarios registrados.
    """
    usuarios = obtener_todos_usuarios()

    return render_template(
        'gestionar_usuarios_admin.html',
        usuarios=usuarios
    )

@gestionar_usuarios_bp.route('/actualizar_rol', methods=['POST'])
def cambiar_rol():
    """Actualiza el rol de un usuario en el sistema.

    Obtiene el identificador del usuario y el nuevo rol desde el
    formulario, junto con el identificador del administrador que realiza
    la acción. Posteriormente ejecuta la actualización del rol y registra
    el resultado mediante mensajes flash. Finalmente redirige a la vista
    de gestión de usuarios.

    Returns:
        Response: Redirección a la vista de gestión de usuarios después
            de procesar la actualización del rol.
    """
    id_usuario = request.form.get('id_usuario')
    nuevo_rol = request.form.get('nuevo_rol')

    # capturamos el ID del admin para guardar en el auditoria
    id_admin_activo = session.get('id_usuario')

    # se regresa el ID del admin como tercer argumento para la auditoria
    resultado = actualizar_rol_usuario(id_usuario, nuevo_rol, id_admin=id_admin_activo)

    if resultado:
        flash("Rol actualizado correctamente", "success")
    else:
        flash("No se pudo actualizar el rol", "error")

    # Redirecciona de vuelta a la lista para ver los resultados actualizados
    return redirect(url_for('gestionar_usuarios.gestionar_usuarios'))


@gestionar_usuarios_bp.route('/eliminar_usuario', methods=['POST'])
def borrar_usuario():
    """Elimina un usuario del sistema.

    Obtiene el identificador del usuario desde el formulario y ejecuta
    la operación de eliminación en la base de datos. Posteriormente,
    notifica el resultado mediante mensajes flash y redirige a la vista
    de gestión de usuarios.

    Returns:
        Response: Redirección a la vista de gestión de usuarios después
            de intentar eliminar el usuario.
    """
    id_usuario = request.form.get('id_usuario')

    resultado = eliminar_usuario(id_usuario)

    if resultado:
        flash("Usuario eliminado correctamente", "success")
    else:
        flash("No se pudo eliminar el usuario", "error")

    return redirect(url_for('gestionar_usuarios.gestionar_usuarios'))