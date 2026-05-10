from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.usuario import verify_user, create_user, user_exists

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        nombre = request.form.get('nombre_usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()

        if not nombre or not contrasena:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('login.html')

        user = verify_user(nombre, contrasena)
        if user:
            session['usuario'] = user['nombre_usuario']
            session['rol'] = user['rol']
            return redirect(url_for('dashboard.home'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'usuario' in session:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        nombre = request.form.get('nombre_usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        confirmar = request.form.get('confirmar_contrasena', '').strip()
        rol = request.form.get('rol', '').strip()

        if not nombre or not contrasena or not confirmar or not rol:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('register.html')

        if contrasena != confirmar:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('register.html')

        if len(contrasena) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('register.html')

        if rol not in ['usuario', 'administrador']:
            flash('Rol no válido.', 'error')
            return render_template('register.html')

        if user_exists(nombre):
            flash('El nombre de usuario ya está en uso.', 'error')
            return render_template('register.html')

        if create_user(nombre, contrasena, rol):
            flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error al crear la cuenta. Intenta de nuevo.', 'error')
            return render_template('register.html')

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('auth.login'))
