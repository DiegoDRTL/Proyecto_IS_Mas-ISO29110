from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pydantic import ValidationError

# Importaciones simuladas de tu arquitectura para cursos
from alchemyClasses.curso import curso_exists, create_course
from Schemas.curso.curso_schemas import Curso_form

# Definimos el blueprint para la gestión de cursos
curso_bp = Blueprint('curso', __name__)

@curso_bp.route('/curso/crear', methods=['GET', 'POST'])
def curso_route_handler():
    # Protección de ruta: Solo usuarios autorizados (ej. profesores o administradores)
    if 'usuario' not in session or session.get('rol') not in ['profesor', 'administrador']:
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        accionBoton = request.form.get('accion')
        datosCurso = request.form.to_dict()
        return procesarCreacion(datosCurso, accionBoton)

    return iniciarCreacionCurso()


def iniciarCreacionCurso():
    """
    Muestra la vista del formulario de creación de curso.
    """
    return render_template('crear_curso.html')


def procesarCreacion(datosCurso, accionBoton):
    """
    Procesa los datos enviados, aplica validaciones de Pydantic,
    verifica duplicados e interactúa con la base de datos.
    """
    # Manejar el botón de cancelar dentro del formulario antes de validar
    if accionBoton == 'cancelar':
        return cancelarCreacion()

    try:
        # Validación de los datos recibidos mediante el esquema de Pydantic
        datos_validados = Curso_form(**datosCurso)

        # Verificar si el curso ya existe en la base de datos utilizando el nombre
        if curso_exists(datos_validados.nombre):
            return manejarErroresValidacion('El nombre del curso ya se encuentra registrado.')

        # Inserción en la base de datos mediante la función del modelo
        # Se asume que create_course maneja la conexión, cursor y commits correspondientes
        creacion_exitosa = create_course(
            nombre=datos_validados.nombre,
            descripcion=datos_validados.descripcion,
            id_profesor=session.get('id_usuario')  # Vincula el curso al profesor logueado
        )

        if not creacion_exitosa:
            return manejarErroresValidacion('Error al guardar el curso en la base de datos. Intente nuevamente.')

        # Mensaje de éxito consistente con el estilo de la aplicación ('realizado')
        flash('Curso creado exitosamente.', 'realizado')
        return redirect(url_for('profesor.gestionar_profesores'))

    except ValidationError as e:
        # Extraer el mensaje de error de Pydantic y pasarlo como codigoError
        codigoError = e.errors()[0]['msg']
        return manejarErroresValidacion(f"Error de validación: {codigoError}")

    except Exception as e:
        return manejarErroresValidacion("Error interno del servidor al procesar la creación del curso.")


def manejarErroresValidacion(codigoError):
    """
    Centraliza las alertas de error y vuelve a pintar el formulario
    manteniendo la consistencia visual de tu app ('error').
    """
    flash(codigoError, 'error')
    return render_template('crear_curso.html')


def cancelarCreacion():
    """
    Aborta el proceso de creación de manera limpia y redirige al panel principal.
    """
    flash('Creación del curso cancelada.', 'info')
    return redirect(url_for('profesor.gestionar_profesores'))