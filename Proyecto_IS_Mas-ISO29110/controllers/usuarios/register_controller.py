"""
Módulo de registro de usuarios.

Este controlador gestiona el proceso de registro de nuevos usuarios en el
sistema, incluyendo la validación de datos, creación de cuentas, manejo de
errores y control del flujo de registro.

Permite iniciar, procesar o cancelar el registro de usuarios.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pydantic import ValidationError

# Importación de las funciones del modelo
from alchemyClasses.usuario import correo_exists, create_user
from Schemas.usuario.user_schemas import User_form

registrarUsuario_bp = Blueprint('register', __name__)


@registrarUsuario_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Gestiona el proceso de registro de nuevos usuarios.

    Redirige al dashboard si el usuario ya se encuentra autenticado.
    Si la solicitud es POST, evalúa si la acción corresponde a una
    cancelación del registro o al procesamiento del formulario de
    creación de usuario. En caso de ser GET, muestra la vista inicial
    del formulario de registro.

    Returns:
        Response: Redirección al dashboard si el usuario ya está
            autenticado, procesamiento del registro si es POST o
            renderizado del formulario de registro si es GET.
    """
    if 'id_usuario' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        if request.form.get('accion') == 'cancelar':
            return cancelarRegistro()

        return procesarRegistro()

    return iniciarProcesoRegistro()

def iniciarProcesoRegistro():
    """Muestra el formulario de registro de usuarios.

    Renderiza la plantilla correspondiente al formulario de registro,
    utilizado cuando el usuario accede mediante una solicitud GET.

    Returns:
        Response: Plantilla del formulario de registro de usuarios.
    """
    return render_template('register.html')

def procesarRegistro():
    """Procesa la creación de un nuevo usuario en el sistema.

    Valida los datos enviados desde el formulario de registro mediante
    un esquema Pydantic. Verifica que el correo no esté previamente
    registrado y, si la validación es exitosa, crea el usuario en la
    base de datos. También gestiona errores de validación y errores
    internos del servidor.

    Returns:
        Response: Redirección al login cuando el registro es exitoso o
            respuesta generada por el manejador de errores en caso de
            fallo de validación o error interno.

    Raises:
        ValidationError: Puede ocurrir durante la validación del esquema
            ``User_form``. Es capturada y manejada internamente.
        Exception: Cualquier otro error inesperado durante el proceso de
            registro es capturado y gestionado.
    """
    try:
        # Extraemos los datos del formulario directamente para asegurar su lectura
        datos_raw = request.form.to_dict()
        datos_validados = User_form(**datos_raw)

        if correo_exists(datos_validados.correo):
            return manejarErrorValidacion('El correo electrónico ya está registrado.')

        registro_exitoso = create_user(
            nombre_usuario=datos_validados.nombre,
            a_paterno=datos_validados.apellido_paterno,
            a_materno=datos_validados.apellido_materno,
            contrasena=datos_validados.contrasena,
            f_nacimiento=datos_validados.fecha_nacimiento,
            rol='alumno',
            correo=datos_validados.correo,
            telefono=datos_validados.telefono
        )

        if not registro_exitoso:
            return manejarErrorValidacion('Error al guardar en la base de datos. Intente nuevamente.')

        # Cambiado a 'error' o 'success' según manejes los estilos CSS de tus alertas flash
        flash(f'Registro exitoso. ID de usuario asignado: {registro_exitoso}', 'success')
        return redirect(url_for('auth.login'))

    except ValidationError as e:
        msg = e.errors()[0]['msg']
        campo = e.errors()[0]['loc'][0]
        return manejarErrorValidacion(f"Error en el campo '{campo}': {msg}")

    except Exception as e:
        print(f"Error interno en el controlador: {e}")
        return manejarErrorValidacion("Error interno del servidor al procesar el registro.")

def manejarErrorValidacion(mensaje):
    """Gestiona errores de validación durante el registro de usuarios.

    Muestra un mensaje de error al usuario mediante el sistema de
    notificaciones flash y vuelve a renderizar la vista de registro
    para permitir corregir los datos ingresados.

    Args:
        mensaje (str): Mensaje descriptivo del error ocurrido durante
            el proceso de registro.

    Returns:
        Response: Plantilla del formulario de registro con el mensaje
            de error correspondiente.
    """
    flash(mensaje, 'error')
    return render_template('register.html')

def cancelarRegistro():
    """Cancela el proceso de registro de usuario.

    Muestra un mensaje informando que el registro fue cancelado y
    redirige al usuario a la pantalla de inicio de sesión.

    Returns:
        Response: Redirección a la vista de login después de cancelar
            el registro.
    """
    flash('Registro cancelado.', 'info')
    return redirect(url_for('auth.login'))