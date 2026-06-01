"""
Módulo de autenticación de usuarios.

Este controlador gestiona el inicio y cierre de sesión del sistema.
Permite autenticar usuarios mediante credenciales, crear sesiones activas
y destruirlas al cerrar sesión.

Incluye validación de usuarios, manejo de sesiones y control de acceso
a rutas protegidas.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.usuario import verify_user, registrar_cierre_sesion

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Redirige al usuario a la página de inicio de sesión.

    Esta ruta actúa como punto de entrada de la aplicación y envía al
    usuario directamente a la vista de autenticación.

    Returns:
        Response: Redirección a la ruta de inicio de sesión.
    """
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Gestiona el inicio de sesión de los usuarios.

    Permite autenticar a un usuario mediante su identificador (ID o
    correo) y contraseña. Si las credenciales son válidas, se crean las
    variables de sesión correspondientes para mantener la autenticación
    activa. En caso contrario, se muestra un mensaje de error.

    Además, si el usuario ya tiene una sesión activa, se redirige
    directamente al panel principal.

    Returns:
        Response: Vista de login en caso de GET o error de autenticación,
            o redirección al panel principal cuando el inicio de sesión
            es exitoso o ya existe una sesión activa.
    """
    if 'id_usuario' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        identificador = request.form.get('identificador', '').strip()
        contrasena = request.form.get('contrasena', '').strip()

        # Validamos que no vengan vacíos
        if not identificador or not contrasena:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('login.html')

        # Pasamos el identificador (puede ser el ID numérico o el correo electrónico)
        user = verify_user(identificador, contrasena)

        if user:
            # SESIÓN PRINCIPAL EN FLASK COOKIES
            session['id_usuario'] = user['id_usuario']

            # ESTO SOLO ES PARA MOSTRAR EL NOMBRE EN EL DASHBOARD
            session['usuario'] = user['nombre']

            # ROL
            session['rol'] = user['rol']

            print('LOGIN EXITOSO')
            print(session)

            return redirect(url_for('dashboard.home'))

        else:
            flash('Usuario o contraseña incorrectos.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Cierra la sesión del usuario autenticado.

    Registra el cierre de sesión en el sistema (si existe un usuario
    autenticado), elimina toda la información almacenada en la sesión
    de Flask y redirige al usuario a la pantalla de inicio de sesión.

    Returns:
        Response: Redirección a la página de login después de cerrar la
            sesión del usuario.
    """
    # Registramos el cierre de sesión antes de limpiar las cookies de Flask
    if 'id_usuario' in session:
        registrar_cierre_sesion(session['id_usuario'])

    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('auth.login'))