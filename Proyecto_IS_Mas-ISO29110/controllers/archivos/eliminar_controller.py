from flask import Blueprint, render_template, request, redirect, url_for, session, flash

# Importamos las funciones del modelo recién estructuradas
from alchemyClasses.archivo import get_archivo, delete_archivo_db

# Definimos el blueprint para la gestión de archivos
archivo_bp = Blueprint('archivo', __name__)

@archivo_bp.route('/archivo/eliminar/<int:id_archivo>', methods=['GET', 'POST'])
def archivo_route_handler(id_archivo):
    """
    Manejador de ruta principal que deriva el flujo según el método HTTP.
    """
    # Protección de ruta: Validar sesión activa
    if 'usuario' not in session:
        flash('Acceso no autorizado. Por favor inicia sesión.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        accionBoton = request.form.get('accion')
        return procesarConfirmacionDeUsuario(id_archivo, accionBoton)

    return solicitarEliminacion(id_archivo)


def solicitarEliminacion(id_archivo):
    """
    Muestra la vista de confirmación antes de proceder al borrado.
    Verifica que el recurso realmente exista antes de pintar la pantalla.
    """
    archivo = get_archivo(id_archivo)
    if not archivo:
        return manejarExcepcionBorado("El archivo que intenta eliminar no existe o ya fue removido.")

    return render_template('eliminar_archivo.html', archivo=archivo)


def procesarConfirmacionDeUsuario(id_archivo, accionBoton):
    """
    Determina el camino a seguir basándose en la decisión final del usuario
    en el formulario (Confirmar / Cancelar).
    """
    if accionBoton == 'cancelar':
        flash('Eliminación del archivo cancelada.', 'info')
        return redirect(url_for('dashboard.home'))

    if accionBoton == 'confirmar':
        return ejecutarBorradoOPuntoFisico(id_archivo)

    return manejarExcepcionBorado("Acción de formulario no reconocida.")


def ejecutarBorradoOPuntoFisico(id_archivo):
    """
    Se conecta con el modelo para ejecutar la sentencia de borrado de forma segura.
    """
    try:
        # Doble verificación de existencia previa
        archivo_existente = get_archivo(id_archivo)
        if not archivo_existente:
            return manejarExcepcionBorado("No se pudo realizar la acción porque el archivo no existe.")

        # Llamada a la función SQL
        borrado_exitoso = delete_archivo_db(id_archivo)

        if not borrado_exitoso:
            return manejarExcepcionBorado("Error crítico en la base de datos al intentar suprimir el registro.")

        # Éxito
        flash('El archivo ha sido eliminado correctamente.', 'realizado')
        return redirect(url_for('dashboard.home'))

    except Exception as e:
        return manejarExcepcionBorado(f"Error inesperado del sistema: {str(e)}")


def manejarExcepcionBorado(codigoError):
    """
    Centraliza el control de fallas lógicas o de infraestructura en el proceso de borrado,
    notificando al usuario.
    """
    flash(codigoError, 'error')
    return redirect(url_for('dashboard.home'))