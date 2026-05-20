from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from pydantic import ValidationError

# Importacion de las funciones
from alchemyClasses.usuario import user_exists, create_user
from Schemas.usuario.user_schemas import User_form

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Si el usuario ya está logueado, redirigir al inicio/dashboard
    if 'usuario' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        # Manejar el botón de cancelar dentro del formulario si el usuario presiona "Cancelar"
        if request.form.get('accion') == 'cancelar':
            return cancelarRegistro()

        return procesarRegistro()

    return iniciarProcesoRegistro()


def iniciarProcesoRegistro():
    """
    Muestra la vista del formulario de registro.
    """
    return render_template('register.html')


def procesarRegistro():
    """
    Procesa los datos enviados, aplica validaciones de Pydantic,
    encripta la contraseña e interactúa con la base de datos.
    """
    try:
        # Conversión de request.form a diccionario para User_form de Pydantic
        datos_raw = request.form.to_dict()
        datos_validados = User_form(**datos_raw)

        # Verificar si el usuario ya existe mediante la función de tu modelo
        # (Adaptado para usar el username, ya que tu get_user busca por ese campo)
        if user_exists(datos_validados.username):
            return manejarErrorValidacion('El usuario ya está registrado.')

        # Encriptamos la contraseña de manera segura antes de guardarla
        password_encriptada = generate_password_hash(datos_validados.password)

        # Crear y persistir el usuario en la BD mediante tu función create_user.
        # Utilizamos .get() para extraer datos de datos_raw en caso de que no existan
        # en tu User_form original, previniendo errores si el formulario está incompleto.
        registro_exitoso = create_user(
            nombre_usuario=datos_validados.username,
            a_paterno=datos_raw.get('a_paterno', ''),
            a_materno=datos_raw.get('a_materno', ''),
            contrasena=password_encriptada,
            f_nacimiento=datos_raw.get('f_nacimiento', '2000-01-01'), # Asegura un formato compatible si está vacío
            rol='usuario', # Rol por defecto para nuevos registros
            correo=datos_validados.correo,
            telefono=datos_raw.get('telefono', '')
        )

        if not registro_exitoso:
            # Si el rollback ocurrió dentro de create_user, devolvemos un error
            return manejarErrorValidacion('Error al guardar en la base de datos. Intente nuevamente.')

        # Mensaje de éxito consistente con el estilo de tus otras vistas ('realizado')
        flash('Registro exitoso. Por favor inicia sesión.', 'realizado')
        return redirect(url_for('auth.login'))

    except ValidationError as e:
        # Extraer el primer mensaje de error específico que gatille Pydantic
        msg = e.errors()[0]['msg']
        return manejarErrorValidacion(f"Error de validación: {msg}")

    except Exception as e:
        # Ya no usamos db.session.rollback() aquí, porque tu función create_user
        # ya implementa su propio conn.rollback() en su bloque except.
        return manejarErrorValidacion("Error interno del servidor al procesar el registro.")


def manejarErrorValidacion(mensaje):
    """
    Centraliza las alertas de error y vuelve a pintar el formulario
    manteniendo la consistencia visual de tu app ('error').
    """
    flash(mensaje, 'error')
    return render_template('register.html')


def cancelarRegistro():
    """
    Aborta el proceso de registro de manera limpia y redirige al login.
    """
    flash('Registro cancelado.', 'info')
    return redirect(url_for('auth.login'))