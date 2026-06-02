"""Módulo de controladores para la eliminación segura de archivos adjuntos.

Este módulo define el Blueprint `eliminar_archivo` y gestiona el flujo de control
para la baja de recursos multimedia vinculados a los cursos, regulando tanto la
confirmación previa del usuario en la interfaz como la llamada a la persistencia.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.archivo import get_archivo, delete_archivo_db
import os
eliminarArchivo_bp = Blueprint('eliminar_archivo', __name__)

@eliminarArchivo_bp.route('/archivo/eliminar/<int:id_archivo>', methods=['GET', 'POST'])
def archivo_route_handler(id_archivo):
    """Manejador de ruta principal que deriva el flujo según el método HTTP.

    Valida preventivamente que el cliente cuente con una sesión activa en el
    servidor. Si la petición es POST, extrae la intención del formulario para
    procesar la confirmación; si es GET, despacha la solicitud de renderizado.

    Args:
        id_archivo (int): Identificador único del archivo que se desea gestionar.

    Returns:
        Response: Redirección a la pantalla de autenticación si no hay sesión,
            o la delegación del flujo a las funciones secundarias del módulo.
    """
    # Protección de ruta: Validar sesión activa
    if 'id_usuario' not in session:
        flash('Acceso no autorizado. Por favor inicia sesión.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        accionBoton = request.form.get('accion')
        return procesarConfirmacionDeUsuario(id_archivo, accionBoton)

    return solicitarEliminacion(id_archivo)


def solicitarEliminacion(id_archivo):
    """Muestra la vista de confirmación en la interfaz antes de borrar.

    Consulta al modelo para comprobar la existencia real del recurso. Si el
    archivo es localizado, sirve la plantilla de confirmación inyectándole los
    metadatos del archivo correspondiente.

    Args:
        id_archivo (int): Identificador numérico del registro del archivo.

    Returns:
        Response: Plantilla HTML 'eliminar_archivo.html' si el recurso existe,
            o redirección al inicio mediante el manejador de excepciones.
    """
    archivo = get_archivo(id_archivo)
    if not archivo:
        return manejarExcepcionBorado("El archivo que intenta eliminar no existe o ya fue removido.")

    return render_template('eliminar_archivo.html', archivo=archivo)


def procesarConfirmacionDeUsuario(id_archivo, accionBoton):
    """Evalúa la acción del formulario basándose en la decisión del usuario.

    Intervienen dos caminos posibles de ejecución: si el usuario presiona
    'cancelar', el proceso aborta devolviendo un aviso; si presiona
    'confirmar', se autoriza la llamada al motor de eliminación física.

    Args:
        id_archivo (int): Identificador numérico del archivo en cuestión.
        accionBoton (str | None): Cadena de texto recuperada del input 'accion'
            del formulario enviado en el POST.

    Returns:
        Response: Redirección al home con estado informativo si se cancela,
            o la ejecución de la baja definitiva en la base de datos.
    """
    if accionBoton == 'cancelar':
        flash('Eliminación del archivo cancelada.', 'info')
        return redirect(url_for('dashboard.home'))

    if accionBoton == 'confirmar':
        return ejecutarBorradoOPuntoFisico(id_archivo)

    return manejarExcepcionBorado("Acción de formulario no reconocida.")


def ejecutarBorradoOPuntoFisico(id_archivo):
    """Conecta con la capa de datos para suprimir el registro de forma segura.

    Realiza una doble validación de consistencia asegurando que el archivo no
    haya sido eliminado por otro subproceso en paralelo y, posteriormente,
    invoca la rutina SQL encargada de eliminar el registro de la base de datos.

    Args:
        id_archivo (int): Clave primaria del archivo a suprimir.

    Returns:
        Response: Redirección al dashboard con un mensaje flash de éxito tras la
            operación, o reenvío al gestor de fallas ante percances de ejecución.
    """
    try:
        # Doble verificación de existencia previa
        archivo_existente = get_archivo(id_archivo)
        if not archivo_existente:
            return manejarExcepcionBorado("No se pudo realizar la acción porque el archivo no existe.")

        if os.path.exists(archivo_existente['ruta']):
            os.remove(archivo_existente['ruta'])
        else:
            return manejarExcepcionBorado("Error al eliminar fisicamente el archivo, no fue posible acceder a la ruta")

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
    """Centraliza e intercepta los fallos lógicos surgidos durante el proceso.

    Notifica al usuario mediante alertas visuales (flash) la razón exacta por
    la cual no pudo completarse el borrado, impidiendo el quiebre abrupto de
    la aplicación web y redirigiéndolo al área principal de forma segura.

    Args:
        codigoError (str): Mensaje o código de error descriptivo del incidente.

    Returns:
        Response: Redirección al endpoint de inicio del dashboard.
    """
    flash(codigoError, 'error')
    return redirect(url_for('dashboard.home'))