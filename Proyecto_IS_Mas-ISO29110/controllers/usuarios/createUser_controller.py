from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.usuario import assign_rol, get_rol_usuarios, get_telefono, get_correo

#definicion del blueprint
create_bp = Blueprint('create', __name__)

@create_bp.route('/usuarios_sr')
def usuarios_sr():
    #en caso de no haberse iniciado aun sesion
    if 'user_id' not in session:
       return redirect(url_for('auth.login'))
    
    rol =session.get('rol')
    usuarios = get_rol_usuarios()

    if rol == 'administrador':
        return render_template('creacion.html', usuarios=usuarios)
    
    else:
        flash('No tienes acceso a esta opcion', 'error')
        redirect(url_for('auth.login'))
    
@create_bp.route('/usuarios_sr/<int:id_usuario>/<str:rol>/crear', methods=['POST'])
def crear_usuario(id_usuario, rol_as):
    #en caso de no haberse iniciado aun sesion
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