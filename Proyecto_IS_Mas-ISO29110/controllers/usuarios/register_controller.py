"""Módulo de autenticación para el registro de nuevos usuarios en la aplicación.

Este módulo define el Blueprint 'register' y gestiona el flujo de registro,
incluyendo la validación de datos con Pydantic, la verificación de correos
duplicados y la persistencia en la base de datos a través de SQLAlchemy.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pydantic import ValidationError

# Importación de las funciones del modelo
from alchemyClasses.usuario import correo_exists, create_user
from Schemas.usuario.user_schemas import User_form

registrarUsuario_bp = Blueprint('register', __name__)


@registrarUsuario_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Gestiona la ruta principal de registro de usuarios.

    Redirige al dashboard si el usuario ya está autenticado. Si la petición
    es POST, evalúa si se canceló la acción o si se debe procesar el formulario.
    Si es GET, inicia el renderizado del formulario.
    """
    if 'id_usuario' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        if request.form.get('accion') == 'cancelar':
            return cancelarRegistro()

        return procesarRegistro()

    return iniciarProcesoRegistro()


def iniciarProcesoRegistro():
    """Renderiza la plantilla del formulario de registro para peticiones GET."""
    return render_template('register.html')


def procesarRegistro():
    """Procesa, valida y almacena los datos enviados en el formulario de registro.

    Pasa los datos crudos del formulario a un esquema de Pydantic (User_form)
    para su validación. Verifica que el correo no esté registrado y crea
    el usuario en la base de datos con la contraseña en texto plano.
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
        flash('Registro exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    except ValidationError as e:
        msg = e.errors()[0]['msg']
        campo = e.errors()[0]['loc'][0]
        return manejarErrorValidacion(f"Error en el campo '{campo}': {msg}")

    except Exception as e:
        print(f"Error interno en el controlador: {e}")
        return manejarErrorValidacion("Error interno del servidor al procesar el registro.")


def manejarErrorValidacion(mensaje):
    """Muestra un mensaje de error mediante flash y vuelve a renderizar el registro."""
    flash(mensaje, 'error')
    return render_template('register.html')


def cancelarRegistro():
    """Cancela el proceso actual de registro y redirige a la pantalla de login."""
    flash('Registro cancelado.', 'info')
    return redirect(url_for('auth.login'))