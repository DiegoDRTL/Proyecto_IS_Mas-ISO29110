from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.curso import Curso

course_bp = Blueprint('course', __name__)

@course_bp.route('/cursos')
def visualizar_cursos():
   if 'user_id' not in session:
       return redirect(url_for('auth.login'))

   rol =session.get('rol')
   id_usuario = session.get('user.id')

   if rol == 'Administrador':
       cursos = Curso.obtener_todos()
   else:
       cursos = Curso.obtener_por_usuario(id_usuario, rol)

    return render_template('cursos.html', cursos=cursos, rol=rol)

