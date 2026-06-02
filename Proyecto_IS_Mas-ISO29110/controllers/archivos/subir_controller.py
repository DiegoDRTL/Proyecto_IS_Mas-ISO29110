"""Módulo de controladores para la subida masiva y validación de archivos.

Este módulo define el Blueprint `subir_archivo`, establece los directorios
físicos de almacenamiento en el servidor web y gestiona el flujo de control
para la carga, validación de cuotas, nombres duplicados e inserción de nuevos
recursos multimedia vinculados a un curso.
"""

import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from alchemyClasses.archivo import archivo_exists
from Schemas.archivos.archivos_schemas import ArchivoModelo

subirArchivo_bp = Blueprint('subir_archivo', __name__)

# Configuración del entorno de almacenamiento local
CARPETA_DESTINO = os.path.join(os.getcwd(), 'subidas')
os.makedirs(CARPETA_DESTINO, exist_ok=True)

# Instancia global del servicio gestor de lógica de archivos
modelo_gestor = ArchivoModelo(CARPETA_DESTINO)


@subirArchivo_bp.errorhandler(413)
def archivo_grande(error):
    """Gestiona archivos que exceden el tamaño máximo permitido.

    Captura la excepción HTTP 413 generada por Flask cuando el usuario
    intenta subir un archivo cuyo tamaño supera el límite configurado
    por la aplicación. Muestra un mensaje de error mediante el sistema
    de notificaciones flash y redirige al usuario al dashboard principal.

    Args:
        error (Exception): Excepción HTTP 413 generada por Flask al
            detectar que el tamaño del archivo excede el límite
            permitido.

    Returns:
        Response: Redirección al dashboard principal con un mensaje
            informando que el archivo supera el tamaño máximo permitido.
    """
    flash("El archivo supera el límite permitido de 16 MB.", "error")
    return redirect(url_for('dashboard.home'))


@subirArchivo_bp.route('/archivo/subir/<int:id_curso>', methods=['GET', 'POST'])
def curso_route_handler(id_curso):
    """Manejador de la ruta principal de subida que deriva el flujo de control.

    Protege el acceso garantizando que únicamente los usuarios con el rol de
    'profesor' y sesión activa interactúen con el endpoint. Administra el payload
    en peticiones POST y despacha la vista de renderizado en peticiones GET.

    Args:
        id_curso (int): Identificador único del curso destino para el archivo.

    Returns:
        Response: Redirección al login en caso de no contar con autorización, o
            la invocación de las subrutinas de procesamiento de archivos.
    """
    # Protección de ruta: Solo usuarios autorizados (profesores)
    if 'id_usuario' not in session or session.get('rol') not in ['profesor']:
        flash('Acceso no autorizado.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        if 'archivo_usuario' not in request.files:
            flash("No se encontro archivo en el formulario.")
            return iniciarSubirArchivo()

        archivo = request.files['archivo_usuario']

        return procesarSubida(archivo, id_curso)

    return iniciarSubirArchivo()


def iniciarSubirArchivo():
    """Renderiza la interfaz visual para la subida de archivos adjuntos.

    Sirve la plantilla HTML que contiene el formulario con codificación multipart
    adecuada para el envío de flujos binarios hacia el backend.

    Returns:
        Response: Plantilla HTML 'subir_archivo.html' procesada por Flask.
    """
    return render_template('subir_archivo.html')


def procesarSubida(archivo, id_curso):
    """Ejecuta la lógica de orquestación, verificación y persistencia de archivos.

    Valida mediante el modelo de datos que no exista otro recurso
    con el mismo nombre de archivo. Transfiere el archivo al
    gestor de almacenamiento físico para escribirlo en disco e indexarlo en la BD.

    Args:
        archivo (FileStorage): Objeto FileStorage binario recuperado de Flask.
        id_curso (int): Clave primaria del curso con el cual se enlazará el recurso.

    Returns:
        Response: Redirección dinámica hacia la vista del listado de archivos del
            curso, inyectando estados visuales ('realizado' o 'error') mediante flash.
    """
    if archivo_exists(archivo.filename):
        return manejarErroresValidacion('El nombre del archivo ya se encuentra registrado.')

    exito, mensaje = modelo_gestor.guardar_y_registrar(archivo, id_curso)

    if exito > -1:
        flash(mensaje, 'realizado')
        return redirect(url_for('visualizar_archivo.visualizar_archivos', id_curso=id_curso))

    else:
        flash(mensaje, 'error')
        return redirect(url_for('visualizar_archivo.visualizar_archivos', id_curso=id_curso))


def manejarErroresValidacion(codigoError):
    """Centraliza el control de errores lógicos surgidos durante el proceso de carga.
    Lanza notificaciones visuales controladas a través de sesiones flash en caso
    de nombres duplicados o fallos de validación, retornando la interfaz al estado original.

    Args:
        codigoError (str): Mensaje descriptivo con la causa de la anomalía detectada.

    Returns:
        Response: Re-renderizado de la plantilla HTML 'subir_archivo.html'.
    """
    flash(codigoError, 'error')
    return render_template('subir_archivo.html')