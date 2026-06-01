"""
Módulo de autenticación y control de acceso.

Este módulo incluye decoradores para proteger rutas del sistema,
verificando la existencia de una sesión activa antes de permitir el acceso
a funcionalidades restringidas.

Se utiliza principalmente para asegurar que los usuarios estén autenticados.
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash
from controllers.usuarios.sistema_servicios_controller import obtener_logs_auditoria, ejecutar_respaldo_database

# Definimos el Blueprint
admin_sistema_bp = Blueprint('admin_sistema', __name__)

def login_required(f):
    """Restringe el acceso a usuarios con sesión autenticada.

    Este decorador verifica que exista un identificador de usuario en la
    sesión actual. Si el usuario no ha iniciado sesión, es redirigido a
    la página de autenticación. En caso contrario, permite la ejecución
    de la función decorada.

    Args:
        f (Callable): Función o vista que será protegida mediante el
            mecanismo de autenticación.

    Returns:
        Callable: Función decorada que valida la existencia de una
            sesión activa antes de ejecutar la lógica original.
    """
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
    """Muestra la interfaz de configuración y los registros de auditoría.

    Verifica que el usuario autenticado tenga el rol de administrador.
    Si la validación es exitosa, obtiene los registros de auditoría del
    sistema y renderiza la vista de administración correspondiente. En
    caso contrario, muestra un mensaje de error y redirige al panel
    principal.

    Returns:
        Response: Plantilla de administración con los registros de
            auditoría cuando el usuario posee permisos suficientes, o
            una redirección al panel principal en caso contrario.
    """
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
    """Genera y descarga un respaldo de la base de datos.

    Verifica que el usuario autenticado posea el rol de administrador.
    Si la validación es exitosa, ejecuta el proceso de generación del
    respaldo y devuelve el archivo resultante para su descarga. En caso
    contrario, muestra un mensaje de error y redirige al panel principal.

    Returns:
        Response: Archivo de respaldo generado para descarga cuando el
            usuario tiene permisos de administrador, o una redirección
            al panel principal cuando la acción no está autorizada.
    """
    rol = str(session.get('rol')).strip().lower()
    if rol != 'administrador':
        flash("Acción no autorizada.", "error")
        return redirect(url_for('dashboard.home'))

    # Llamamos a la función que ejecuta el respaldo de la base de datos
    return ejecutar_respaldo_database()