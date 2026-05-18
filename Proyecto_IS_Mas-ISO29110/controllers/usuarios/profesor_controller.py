from flask import Blueprint, render_template, redirect, url_for, session, flash
from alchemyClasses.usuario import obtener_profesores, eliminar_usuario

profesor_bp = Blueprint('profesor', __name__)

@profesor_bp.route('/profesores')
def gestionar_profesores():
    if 'usuario' not in session or session.get('rol') != 'administrador':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('auth.login'))

    profesores = obtener_profesores()
    return render_template('profesores.html', profesores=profesores)

@profesor_bp.route('/profesores/<int:id_usuario>/eliminar', methods=['POST'])
def eliminar_profesor(id_usuario):
    if 'usuario' not in session or session.get('rol') =! 'administrador':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('auth.login'))

    exito = eliminar_usuario(id_usuario)

    if exito:
        flash('Profesor eliminado correctamente', 'realizado')
    else:
        flash('No se pudo eliminar el profesor, intente nuevamente', 'error')

    return redirect(url_for('profesor.gestionar_profesores'))

