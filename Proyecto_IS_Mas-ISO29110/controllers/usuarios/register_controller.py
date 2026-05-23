from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from pydantic import ValidationError

# Importación de las funciones del modelo (Cambiamos user_exists por correo_exists)
from alchemyClasses.usuario import correo_exists, create_user
from Schemas.usuario.user_schemas import User_form

registrarUsuario_bp = Blueprint('register', __name__)

@registrarUsuario_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'usuario' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        if request.form.get('accion') == 'cancelar':
            return cancelarRegistro()

        return procesarRegistro()

    return iniciarProcesoRegistro()


def iniciarProcesoRegistro():
    return render_template('register.html')


def procesarRegistro():
    try:
        datos_raw = request.form.to_dict()
        datos_validados = User_form(**datos_raw)

        if correo_exists(datos_validados.correo):
            return manejarErrorValidacion('El correo electrónico ya está registrado.')

        # 1. COMENTAMOS LA ENCRIPCIÓN PARA EVITAR EL TEXTO LARGO
        # password_encriptada = generate_password_hash(datos_validados.contrasena)

        # 2. ENVIAMOS LA CONTRASEÑA EN TEXTO PLANO DIRECTAMENTE
        registro_exitoso = create_user(
            nombre_usuario=datos_validados.nombre,
            a_paterno=datos_validados.apellido_paterno,
            a_materno=datos_validados.apellido_materno,
            contrasena=datos_validados.contrasena,  # <-- Usamos la variable directa aquí
            f_nacimiento=datos_validados.fecha_nacimiento,
            rol='usuario',
            correo=datos_validados.correo,
            telefono=datos_validados.telefono
        )

        if not registro_exitoso:
            return manejarErrorValidacion('Error al guardar en la base de datos. Intente nuevamente.')

        flash('Registro exitoso. Por favor inicia sesión.', 'realizado')
        return redirect(url_for('auth.login'))

    except ValidationError as e:
        msg = e.errors()[0]['msg']
        campo = e.errors()[0]['loc'][0]
        return manejarErrorValidacion(f"Error en el campo '{campo}': {msg}")

    except Exception as e:
        print(f"❌ Error interno en el controlador: {e}")
        return manejarErrorValidacion("Error interno del servidor al procesar el registro.")

def manejarErrorValidacion(mensaje):
    flash(mensaje, 'error')
    return render_template('register.html')


def cancelarRegistro():
    flash('Registro cancelado.', 'info')
    return redirect(url_for('auth.login'))