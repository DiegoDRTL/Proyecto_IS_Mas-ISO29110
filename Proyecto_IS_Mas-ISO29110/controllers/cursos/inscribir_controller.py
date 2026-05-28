from flask import Blueprint, request, redirect, url_for, flash, session
from alchemyClasses.curso import inscribir_alumno
from alchemyClasses.curso import dar_baja_curso

inscribir_bp = Blueprint('inscribir', __name__)

@inscribir_bp.route('/inscribir', methods=['POST'])
def inscribir():
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    try:
        id_usuario = session['id_usuario']  # SALE DE SESIÓN
        identificador_curso = request.form.get('id_curso')

        if not identificador_curso:
            flash("Selecciona un curso", "error")
            return redirect(url_for('dashboard.home'))

        # convertir si es número
        try:
            identificador_curso = int(identificador_curso)
        except ValueError:
            pass

        resultado = inscribir_alumno(id_usuario, identificador_curso)

        if resultado:
            flash("Inscripción realizada correctamente", "success")
        else:
            flash("No se pudo inscribir al curso", "error")

    except Exception as e:
        print(e)
        flash("Error interno", "error")

    return redirect(url_for('dashboard.home'))

@inscribir_bp.route('/dar_baja', methods=['POST'])
def dar_baja():

    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    try:

        id_usuario = session['id_usuario']
        id_curso = request.form.get('id_curso')

        resultado = dar_baja_curso(id_usuario, id_curso)

        if resultado:
            flash("Te diste de baja del curso", "success")
        else:
            flash("No se pudo dar de baja", "error")

    except Exception as e:
        print(e)
        flash("Error interno", "error")

    return redirect(url_for('dashboard.home'))