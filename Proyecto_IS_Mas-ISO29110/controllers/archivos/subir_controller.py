from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os

from alchemyClasses.archivo import archivo_exists
from Schemas.archivos.archivos_schemas import ArchivoModelo

# Definimos el blueprint
subirArchivo_bp = Blueprint('subir_archivo', __name__)

CARPETA_DESTINO = os.path.join(os.getcwd(), 'subidas')
os.makedirs(CARPETA_DESTINO, exist_ok=True) #En caso de no existir la carpeta

# subirArchivo_bp.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Esta linea va en app.py

modelo_gestor = ArchivoModelo(CARPETA_DESTINO)

@subirArchivo_bp.errorhandler(413)
def archivo_grande(error):
    flash("El archivo supera el limite de 16MB")
    return redirect(url_for('archivos.visualizar_archivos')), 413

@subirArchivo_bp.route('/archivo/subir/<int:id_curso>', methods=['GET', 'POST'])
def curso_route_handler(id_curso):
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
    """
    Muestra la vista para subir un archivo.
    """
    return render_template('subir_archivo.html')


def procesarSubida(archivo, id_curso):
    if archivo_exists(archivo.filename):
            return manejarErroresValidacion('El nombre del archivo ya se encuentra registrado.')

    exito, mensaje = modelo_gestor.guardar_y_registrar(archivo, id_curso)

    if exito>-1:
        flash(mensaje, 'realizado')
        return redirect(url_for('visualizar_archivo.visualizar_archivos', id_curso=id_curso))

    else:
        flash(mensaje, 'error')
        return redirect(url_for('visualizar_archivo.visualizar_archivos', id_curso=id_curso))



def manejarErroresValidacion(codigoError):
    """
    Centraliza las alertas de error y vuelve a pintar el formulario
    manteniendo la consistencia visual de tu app ('error').
    """
    flash(codigoError, 'error')
    return render_template('subir_archivo.html')