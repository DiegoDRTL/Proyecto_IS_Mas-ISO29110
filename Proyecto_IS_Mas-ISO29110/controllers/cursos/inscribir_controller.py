"""
Módulo de inscripción y baja de cursos.

Este controlador gestiona la inscripción de usuarios a cursos y la baja
de los mismos. Permite a los alumnos registrarse en cursos disponibles y
retirarse cuando lo deseen, validando siempre la sesión activa.

Incluye manejo de errores, validación de datos de entrada y comunicación
de resultados mediante mensajes flash.
"""

from flask import Blueprint, request, redirect, url_for, flash, session
from alchemyClasses.curso import inscribir_alumno
from alchemyClasses.curso import dar_baja_curso

inscribir_bp = Blueprint('inscribir', __name__)

@inscribir_bp.route('/inscribir', methods=['POST'])
def inscribir():
    """Procesa la inscripción de un alumno a un curso.

    Verifica que exista una sesión activa, obtiene el identificador del
    usuario autenticado y el curso seleccionado desde el formulario,
    valida la información recibida y ejecuta el proceso de inscripción.
    Además, informa al usuario sobre el resultado de la operación
    mediante mensajes flash.

    Returns:
        Response: Redirección al inicio de sesión cuando no existe una
            sesión activa, o al panel principal después de procesar la
            solicitud de inscripción.

    Raises:
        Exception: Cualquier excepción generada durante el proceso de
            inscripción es capturada y gestionada internamente.
    """
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
    """Procesa la baja de un alumno de un curso.

    Verifica que exista una sesión activa, obtiene el identificador del
    usuario autenticado y el curso seleccionado, y ejecuta la operación
    de baja del curso correspondiente. Además, informa al usuario sobre
    el resultado de la operación mediante mensajes flash.

    Returns:
        Response: Redirección al inicio de sesión cuando no existe una
            sesión activa, o al panel principal después de procesar la
            solicitud de baja.

    Raises:
        Exception: Cualquier excepción generada durante el proceso de
            baja es capturada y gestionada internamente.
    """
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