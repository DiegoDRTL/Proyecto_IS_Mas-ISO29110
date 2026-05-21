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
        id_usuario = request.form.get('id_usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()

        if not id_usuario or not contrasena:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('login.html')

        user = verify_user(id_usuario, contrasena)
        if user:
            session['id_usuario'] = user['id_usuario']
            session['rol'] = user['rol']
            return redirect(url_for('dashboard.home'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('auth.login'))
