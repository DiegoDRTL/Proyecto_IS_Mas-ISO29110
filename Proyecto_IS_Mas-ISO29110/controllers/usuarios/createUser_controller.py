"""
Módulo de creación y registro de usuarios.

Este controlador gestiona el flujo de registro de nuevos usuarios en el sistema,
incluyendo la validación de datos mediante Pydantic, verificación de correos
duplicados, creación de usuarios en la base de datos y manejo de errores de
validación.

También permite iniciar el proceso de registro, procesarlo y cancelarlo,
asegurando que los datos ingresados sean consistentes antes de ser almacenados.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.usuario import assign_rol, get_rol_usuarios, get_telefono, get_correo

#definicion del blueprint
create_bp = Blueprint('create', __name__)

@create_bp.route('/usuarios_sr')
def usuarios_sr():
    """Muestra la vista de gestión/creación de usuarios según el rol.

    Verifica que exista una sesión activa y obtiene el rol del usuario
    autenticado. Si el usuario es administrador, permite acceder a la
    vista de creación de usuarios junto con la información necesaria.
    En caso contrario, muestra un mensaje de acceso denegado.

    Returns:
        Response: Vista de creación de usuarios para administradores o
            redirección al login cuando no existe sesión activa.
    """
    # en caso de no haberse iniciado aun sesion
    if 'user_id' not in session:
       return redirect(url_for('auth.login'))
    
    rol =session.get('rol')
    usuarios = get_rol_usuarios()

    if rol == 'administrador':
        return render_template('creacion.html', usuarios=usuarios)
    
    else:
        flash('No tienes acceso a esta opcion', 'error')
        redirect(url_for('auth.login'))
            
@create_bp.route('/usuarios_sr/<int:id_usuario>/<string:rol_as>/crear', methods=['POST'])
def crear_usuario(id_usuario, rol_as):
    """Asigna un rol a un usuario existente.

    Verifica que exista una sesión activa y que el usuario autenticado
    tenga permisos de administrador. Si cumple con los permisos, asigna
    el rol indicado al usuario seleccionado y notifica el resultado de
    la operación. En caso contrario, deniega el acceso.

    Args:
        id_usuario (int): Identificador del usuario al que se le asignará
            un rol.
        rol_as (str): Rol que será asignado al usuario.

    Returns:
        Response: Redirección a la vista de usuarios cuando la operación
            se procesa correctamente, o redirección al login si no hay
            sesión activa.
    """
    # en caso de no haberse iniciado aun sesion
    if 'user_id' not in session:
       return redirect(url_for('auth.login'))
    
    rol =session.get('rol')

    if rol == 'administrador':
        exito = assign_rol(id_usuario, rol_as)
        if exito:
            flash('Creacion realizada con exito', 'realizado')
        else:
            flash('No se pudo crear el usuario, intente nuevamente', 'error')

        return redirect(url_for('create.usuarios_sr'))

    
    else:
        flash('No tienes acceso a esta opcion', 'error')
        redirect(url_for('auth.login'))