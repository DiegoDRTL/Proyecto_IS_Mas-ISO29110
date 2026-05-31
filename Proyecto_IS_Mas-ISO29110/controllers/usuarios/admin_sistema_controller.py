from flask import Blueprint, render_template, session, redirect, url_for, flash
from controllers.usuarios.sistema_servicios_controller import obtener_logs_auditoria, ejecutar_respaldo_database

# Definimos el Blueprint
admin_sistema_bp = Blueprint('admin_sistema', __name__)

def login_required(f):
    """Decorador para proteger que solo entren usuarios autenticados."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_sistema_bp.route('/admin/configuracion')
@login_required
def ver_logs():
    """Ruta que muestra la interfaz de configuración y logs al Administrador."""
    # Verificamos que realmente sea un administrador
    rol = str(session.get('rol')).strip().lower()
    if rol != 'administrador':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('dashboard.home'))

    logs = obtener_logs_auditoria()
    nombre_usuario = session.get('nombre') or session.get('usuario')

    return render_template(
        'admin_gestion_sistema.html',
        logs=logs,
        nombre=nombre_usuario,
        rol=rol
    )

@admin_sistema_bp.route('/admin/respaldo')
@login_required
def descargar_respaldo():
    """Ruta que dispara la descarga del archivo .sql creado por tu servicio."""
    rol = str(session.get('rol')).strip().lower()
    if rol != 'administrador':
        flash("Acción no autorizada.", "error")
        return redirect(url_for('dashboard.home'))

    # Llamamos a la función que ejecuta el respaldo de la base de datos
    return ejecutar_respaldo_database()