from flask import Blueprint, render_template, redirect, url_for, session, flash
from alchemyClasses.archivo import Archivo
from alchemyClasses.curso import Curso

archivo_bp = Blueprint('archivo', __name__)

@archivo_bp.route('/cursos/<int:id_curso>/archivos')
def visualizar_archivos(id_curso):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    curso = Curso.obtener_por_id(id_curso)
    if not curso:
        flash('Curso no existe', 'error') 
        return redirect(url_for('course.visualizar_cursos'))

    archivos = Archivo.obtener_por_curso(id_curso)
    rol = session.get('rol')

    return render_template(
        'archivos.html',
        archivos=archivos,
        curso=curso,
        rol=rol
    )

@archivo_dp.route('/cursos/<int:id_curso>/archivos/<int:id_archivo')
def detalle_archivo(id_curso, id_archivo):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

        archivo = Archivo.obtener_por_id(id_archivo)
        curso = Curso.obtener_por_id(id_curso)
        rol = session.get('rol')

        return render_template(
            'detalle_archivo.html'
            archivo=archivo,
            curso=curso,
            rol=rol
        )