from flask import Blueprint, render_template, request, redirect, url_for, flash

from alchemyClasses.usuario import (
    obtener_todos_usuarios,
    actualizar_rol_usuario,
    eliminar_usuario
)

gestionar_usuarios_bp = Blueprint(
    'gestionar_usuarios',
    __name__
)

# =========================
# Vista principal
# =========================
@gestionar_usuarios_bp.route('/gestionar_usuarios')
def gestionar_usuarios():

    usuarios = obtener_todos_usuarios()

    return render_template(
        'gestionar_usuarios_admin.html',
        usuarios=usuarios
    )


# =========================
# Cambiar rol
# =========================
@gestionar_usuarios_bp.route('/actualizar_rol', methods=['POST'])
def cambiar_rol():

    id_usuario = request.form.get('id_usuario')
    nuevo_rol = request.form.get('nuevo_rol')

    resultado = actualizar_rol_usuario(id_usuario, nuevo_rol)

    if resultado:
        flash("Rol actualizado correctamente", "success")
    else:
        flash("No se pudo actualizar el rol", "error")

    return redirect(url_for('gestionar_usuarios.gestionar_usuarios'))


# =========================
# Eliminar usuario
# =========================
@gestionar_usuarios_bp.route('/eliminar_usuario', methods=['POST'])
def borrar_usuario():

    id_usuario = request.form.get('id_usuario')

    resultado = eliminar_usuario(id_usuario)

    if resultado:
        flash("Usuario eliminado correctamente", "success")
    else:
        flash("No se pudo eliminar el usuario", "error")

    return redirect(url_for('gestionar_usuarios.gestionar_usuarios'))