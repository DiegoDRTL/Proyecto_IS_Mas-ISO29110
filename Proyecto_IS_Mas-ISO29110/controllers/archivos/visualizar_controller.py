from flask import Blueprint, render_template, redirect, url_for, session, flash
from alchemyClasses.archivo import obtener_por_curso, obtener_por_id
from alchemyClasses.curso import obtener_por_id as obtener_curso_por_id


visualizarArchivo_bp = Blueprint('visualizar_archivo', __name__)

@visualizarArchivo_bp.route('/cursos/<int:id_curso>/archivos')
def visualizar_archivos(id_curso):
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    curso_actual = obtener_curso_por_id(id_curso)
    if not curso_actual:
        flash('Curso no existe', 'error')
        return redirect(url_for('course.visualizar_cursos'))

    archivos = obtener_por_curso(id_curso)
    rol = session.get('rol')

    return render_template(
        'archivos.html',
        archivos=archivos,
        curso=curso_actual,
        rol=rol
    )

@visualizarArchivo_bp.route('/cursos/<int:id_curso>/archivos/<int:id_archivo>')
def detalle_archivo(id_curso, id_archivo):
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    curso_actual = obtener_curso_por_id(id_curso)

    if not curso_actual:
        flash('Curso no existe', 'error')
        return redirect(url_for('course.visualizar_cursos'))

    archivo = obtener_por_id(id_archivo)
    if not archivo:
        flash('Archivo no existe', 'error')
        return redirect(url_for('visualizar_archivo.visualizar_archivos', id_curso=id_curso))

    rol = session.get('rol')
    

    return render_template(
        'detalle_archivo.html',
        archivo=archivo,
        curso=curso_actual,
        rol=rol
    )