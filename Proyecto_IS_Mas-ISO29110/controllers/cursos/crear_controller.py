"""
Módulo de gestión de cursos del sistema.

Este controlador maneja todo el ciclo de vida de los cursos dentro de la
plataforma, incluyendo su creación, edición, actualización, cambio de estado
y validación de datos.

Funciones principales del módulo:

- Creación de cursos con validación mediante Pydantic.
- Cambio de estado entre "Abierto" y "Cerrado".
- Edición de cursos únicamente en estado permitido.
- Actualización de información de cursos existentes.
- Manejo de errores de validación y mensajes al usuario.
- Control de acceso basado en sesión y roles (profesor y administrador).

El módulo interactúa con la capa de base de datos a través de funciones
como creación, actualización, consulta y verificación de existencia de cursos,
asegurando la integridad de los datos antes de persistirlos.

También gestiona el flujo de la interfaz de usuario mediante renderizado de
plantillas y redirecciones según el estado de la operación.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pydantic import ValidationError

# Agregamos "update_course_status" a tus importaciones de base de datos
from alchemyClasses.curso import curso_exists, create_course, update_course_status, update_course_data, obtener_por_id
from Schemas.curso.curso_schemas import Curso_form

crearCurso_bp = Blueprint('curso', __name__)

@crearCurso_bp.route('/curso/crear', methods=['GET', 'POST'])
def curso_route_handler():
    """Gestiona la creación de cursos mediante solicitudes GET y POST.

    Verifica que el usuario tenga una sesión activa y cuente con los
    permisos necesarios para crear cursos. En solicitudes POST procesa
    los datos enviados desde el formulario, realiza la limpieza y
    validación básica de los campos, y delega la creación del curso a la
    función correspondiente. En solicitudes GET inicia el flujo de
    creación de cursos.

    Returns:
        Response: Respuesta HTTP correspondiente al resultado de la
            operación solicitada, ya sea redirección, procesamiento de
            creación o renderizado de la vista de creación.

    Raises:
        ValueError: Puede ocurrir durante la conversión del campo
            capacidad a entero, aunque es manejada internamente.
    """
    if 'id_usuario' not in session or session.get('rol') not in ['profesor', 'administrador']:
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        accionBoton = request.form.get('accion')

        if accionBoton == 'cancelar':
            return cancelarCreacion()

        # Extraccion y limpieza de los campos
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

@crearCurso_bp.route('/curso/cambiar-estado', methods=['POST'])
def cambiar_estado_route_handler():
    """Cambia el estado de un curso entre abierto y cerrado.

    Verifica que el usuario tenga una sesión activa y los permisos
    necesarios para realizar la operación. Obtiene el identificador
    del curso y su estado actual desde el formulario, determina el
    nuevo estado correspondiente y actualiza la información en la
    base de datos. Finalmente, informa el resultado mediante mensajes
    flash y redirige al panel principal.

    Returns:
        Response: Redirección al panel principal después de procesar
            la solicitud, independientemente del resultado de la
            operación.
    """
    # Validación de seguridad del Rol
    if 'id_usuario' not in session or session.get('rol') not in ['profesor', 'administrador']:
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('auth.login'))

    id_curso = request.form.get('id_curso')
    estado_actual = (request.form.get('estado_actual') or '').strip().lower()

    # Determinamos el estado contrario.
    if estado_actual in ['abierto', 'disponible']:
        nuevo_estado = 'Cerrado'
    else:
        nuevo_estado = 'Abierto'

    if id_curso:
        # Ejecutamos la consulta en la base de datos
        exito = update_course_status(id_curso, nuevo_estado)

        if exito:
            flash(f'El estado del curso #{id_curso} se actualizó a "{nuevo_estado}".', 'realizado')
        else:
            flash('Error al intentar cambiar el estado del curso en la base de datos.', 'error')
    else:
        flash('No se proporcionó un ID de curso válido.', 'error')

    # Redireccionamos de vuelta al panel de control donde están las tarjetas
    return redirect(url_for('dashboard.home'))

@crearCurso_bp.route('/curso/editar/<int:id_curso>', methods=['GET'])
def editar_curso_handler(id_curso):
    """Muestra la vista de edición de un curso específico.

    Verifica que el usuario tenga una sesión activa y cuente con los
    permisos necesarios para editar cursos. Recupera la información
    del curso a partir de su identificador y valida que se encuentre
    en estado "Cerrado", ya que únicamente los cursos en dicho estado
    pueden ser modificados. Posteriormente adapta el nombre del curso
    para su uso en la plantilla y renderiza la vista de edición.

    Args:
        id_curso (int): Identificador único del curso que se desea editar.

    Returns:
        Response: Plantilla de edición del curso cuando la operación es
            válida, o una redirección al inicio de sesión o al panel
            principal en caso de error o falta de permisos.
    """
    if 'id_usuario' not in session or session.get('rol') not in ['profesor', 'administrador']:
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('auth.login'))

    curso = obtener_por_id(id_curso)

    print("DEBUG CURSO DICT:", curso)

    if not curso or curso['estado'].lower() != 'cerrado':
        flash('Solo se pueden modificar cursos en estado "Cerrado" (Borrador).', 'error')
        return redirect(url_for('dashboard.home'))

    # utilizando el campo 'curso_nombre' que almacena tu lógica interna de base de datos
    if curso and 'curso_nombre' in curso:
        curso['nombre'] = curso['curso_nombre']

    return render_template('editar_curso.html', curso=curso)

@crearCurso_bp.route('/curso/actualizar', methods=['POST'])
def actualizar_curso_backend():
    """Actualiza la información de un curso existente.

    Verifica que el usuario tenga una sesión activa y cuente con los
    permisos necesarios para realizar modificaciones. Obtiene los datos
    enviados desde el formulario, realiza la conversión y limpieza de los
    campos recibidos, valida la información mediante un modelo Pydantic
    y actualiza los datos del curso en la base de datos. En caso de que
    la validación falle, informa el error al usuario y lo redirige a la
    vista de edición correspondiente.

    Returns:
        Response: Redirección al panel principal cuando la actualización
            se realiza o procesa correctamente, o redirección a la vista
            de edición si ocurre un error de validación.

    Raises:
        ValidationError: Puede producirse durante la validación de los
            datos mediante el modelo ``Curso_form``. La excepción es
            capturada y gestionada internamente.
    """
    if 'id_usuario' not in session or session.get('rol') not in ['profesor', 'administrador']:
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('auth.login'))

    id_curso = request.form.get('id_curso')
    nombre = (request.form.get('nombre') or '').strip()
    capacidad_raw = (request.form.get('capacidad') or '').strip()
    descripcion = (request.form.get('descripcion') or '').strip()

    try:
        capacidad = int(capacidad_raw) if capacidad_raw.isdigit() else None
    except ValueError:
        capacidad = None

    datos_procesados = {
        'nombre': nombre if nombre != '' else None,
        'capacidad': capacidad,
        'estado': 'Cerrado', # Mantiene el estado de borrador/cerrado al editar
        'descripcion': descripcion if descripcion != '' else None
    }

    try:
        # Volvemos a usar Pydantic para garantizar que cumpla las reglas de negocio
        datos_validados = Curso_form(**datos_procesados)

        exito = update_course_data(id_curso, datos_validados.nombre, datos_validados.capacidad, datos_validados.descripcion)

        if exito:
            flash('Borrador del curso actualizado correctamente.', 'realizado')
        else:
            flash('Error al actualizar los datos en la base de datos.', 'error')

        return redirect(url_for('dashboard.home'))

    except ValidationError as e:
        error_detalle = e.errors()[0]
        flash(f"Error en campo '{error_detalle.get('loc')[0]}': {error_detalle.get('msg')}", 'error')
        return redirect(url_for('curso.editar_curso_handler', id_curso=id_curso))

def iniciarCreacionCurso():
    """Muestra la vista para la creación de un nuevo curso.

    Obtiene el nombre del usuario autenticado desde la sesión y lo
    envía a la plantilla correspondiente para personalizar la interfaz
    de creación de cursos.

    Returns:
        Response: Plantilla de creación de curso renderizada con la
            información del usuario actual.
    """
    nombre_usuario = session.get('nombre') or session.get('usuario')
    return render_template('crear_curso.html', nombre=nombre_usuario)

def procesarCreacion(datosCurso):
    """Procesa la creación de un nuevo curso.

    Valida los datos recibidos mediante un modelo Pydantic, verifica que
    no exista previamente un curso con el mismo nombre y registra el
    nuevo curso en la base de datos. Además, gestiona los mensajes de
    éxito o error correspondientes y redirige al usuario según el
    resultado de la operación.

    Args:
        datosCurso (dict): Diccionario que contiene los datos del curso
            previamente procesados y preparados para validación.

    Returns:
        Response: Redirección al panel principal cuando la creación es
            exitosa o respuesta generada por el manejador de errores en
            caso de validación fallida o error interno.

    Raises:
        ValidationError: Puede producirse durante la validación de los
            datos mediante el modelo ``Curso_form``. La excepción es
            capturada y gestionada internamente.
        Exception: Cualquier excepción no controlada durante el proceso
            de creación es capturada y gestionada internamente.
    """
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
    """Gestiona los errores de validación durante la creación de cursos.

    Muestra un mensaje de error al usuario mediante el sistema de
    notificaciones flash y vuelve a renderizar la vista de creación
    de cursos conservando la información del usuario autenticado.

    Args:
        codigoError (str): Mensaje descriptivo del error que será
            mostrado al usuario.

    Returns:
        Response: Plantilla de creación de curso renderizada junto con
            el mensaje de error correspondiente.
    """
    flash(codigoError, 'error')
    nombre_usuario = session.get('nombre') or session.get('usuario')
    return render_template('crear_curso.html', nombre=nombre_usuario)

def cancelarCreacion():
    """Cancela el proceso de creación de un curso.

    Informa al usuario que la operación de creación fue cancelada y lo
    redirige al panel principal de la aplicación.

    Returns:
        Response: Redirección al panel principal después de cancelar la
            creación del curso.
    """
    flash('Creación del curso cancelada.', 'success')
    return redirect(url_for('dashboard.home'))