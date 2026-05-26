from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pydantic import ValidationError

from alchemyClasses.curso import curso_exists, create_course
from Schemas.curso.curso_schemas import Curso_form

crearCurso_bp = Blueprint('curso', __name__)

@crearCurso_bp.route('/curso/crear', methods=['GET', 'POST'])
def curso_route_handler():
    if 'id_usuario' not in session or session.get('rol') not in ['profesor', 'administrador']:
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        accionBoton = request.form.get('accion')

        if accionBoton == 'cancelar':
            return cancelarCreacion()

        # 🛠️ EXTRACCIÓN EXPLÍCITA Y LIMPIEZA DE CAMPOS
        nombre = (request.form.get('nombre') or '').strip()
        capacidad_raw = (request.form.get('capacidad') or '').strip()
        estado = (request.form.get('estado') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()

        # 📋 IMPRESIÓN DE DEPURACIÓN EN TERMINAL
        print("======== DATOS RECIBIDOS DEL FORMULARIO ========")
        print(f"Nombre extraído: '{nombre}'")
        print(f"Capacidad extraída: '{capacidad_raw}'")
        print(f"Estado extraído: '{estado}'")
        print(f"Descripción extraída: '{descripcion}'")
        print("=================================================")

        # Conversión explícita a entero para evitar problemas de tipado estricto en Pydantic
        try:
            capacidad = int(capacidad_raw) if capacidad_raw.isdigit() else None
        except ValueError:
            capacidad = None

        # Construimos el diccionario final incluyendo el nuevo campo requerido
        datos_procesados = {
            'nombre': nombre if nombre != '' else None,
            'capacidad': capacidad,
            'estado': estado if estado != '' else None,
            'descripcion': descripcion if descripcion != '' else None
        }

        return procesarCreacion(datos_procesados)

    return iniciarCreacionCurso()


def iniciarCreacionCurso():
    nombre_usuario = session.get('nombre') or session.get('usuario')
    return render_template('crear_curso.html', nombre=nombre_usuario)


def procesarCreacion(datosCurso):
    try:
        # Alimentamos a Pydantic con los campos explícitamente limpios y tipados
        datos_validados = Curso_form(**datosCurso)

        if curso_exists(datos_validados.nombre):
            return manejarErroresValidacion('El nombre del curso ya se encuentra registrado.')

        # CAMPO VALIDADO AL MODELO DE DATA
        id_curso_nuevo = create_course(
            nombre=datos_validados.nombre,
            capacidad=datos_validados.capacidad,
            estado=datos_validados.estado,
            descripcion=datos_validados.descripcion,
            id_usuario=session.get('id_usuario')
        )

        # Captura de manera segura si la inserción devuelve False o None
        if not id_curso_nuevo:
            return manejarErroresValidacion('Error al guardar el curso en la base de datos. Intente nuevamente.')

        if id_curso_nuevo is True:
            flash('Curso creado exitosamente.', 'realizado')
        else:
            flash(f'Curso creado exitosamente con el ID: {id_curso_nuevo}.', 'realizado')

        return redirect(url_for('dashboard.home'))

    except ValidationError as e:
        error_detalle = e.errors()[0]
        campo_afectado = error_detalle.get('loc')[0]
        mensaje_error = error_detalle.get('msg')

        return manejarErroresValidacion(f"Error en campo '{campo_afectado}': {mensaje_error}")

    except Exception as e:
        print(f"Error detectado en el controlador de cursos: {e}")
        return manejarErroresValidacion("Error interno del servidor al procesar la creación del curso.")


def manejarErroresValidacion(codigoError):
    flash(codigoError, 'error')
    nombre_usuario = session.get('nombre') or session.get('usuario')
    return render_template('crear_curso.html', nombre=nombre_usuario)

def cancelarCreacion():
    flash('Creación del curso cancelada.', 'success')
    return redirect(url_for('dashboard.home'))