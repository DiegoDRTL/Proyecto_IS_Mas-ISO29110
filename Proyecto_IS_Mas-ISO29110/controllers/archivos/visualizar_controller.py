"""Módulo de controladores para la visualización, descarga y renderizado de archivos.

Este módulo define el Blueprint `visualizar_archivo` y gestiona los endpoints
públicos y privados para listar los archivos adjuntos de un curso, inspeccionar
el registro de un archivo en particular y transmitir flujos binarios directamente
al navegador web del usuario mediante funciones de descarga controladas.
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash, send_file
from alchemyClasses.archivo import obtener_por_curso, obtener_por_id
from alchemyClasses.curso import obtener_por_id as obtener_curso_por_id

visualizarArchivo_bp = Blueprint('visualizar_archivo', __name__)

@visualizarArchivo_bp.route('/cursos/<int:id_curso>/archivos')
def visualizar_archivos(id_curso):
    """Muestra el listado completo de archivos vinculados a un curso específico.

    Se asegura de que exista una sesión de usuario activa y confirma la existencia
    operativa del curso en la base de datos antes de recuperar e inyectar los
    archivos adjuntos en la plantilla de la interfaz de usuario.

    Args:
        id_curso (int): Identificador único del curso cuyos archivos se desean listar.

    Returns:
        Response: Redirección al login si el usuario no está autenticado o al
            catálogo de cursos si el identificador no coincide con un registro,
            en caso contrario renderiza la plantilla HTML 'archivos.html'.
    """
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    # Validación: Si el curso ya fue eliminado de la BD, curso_actual será None
    curso_actual = obtener_curso_por_id(id_curso)
    if not curso_actual:
        flash('Curso no existe', 'error')
        return redirect(url_for('visualizar_curso.visualizar_cursos'))

    archivos = obtener_por_curso(id_curso)
    rol = session.get('rol')

    return render_template(
        'archivos.html',
        archivos=archivos,
        curso=curso_actual,
        rol=rol
    )


@visualizarArchivo_bp.route('/cursos/<int:id_curso>/archivos/<int:id_archivo>')
def detalle_archivo(id_curso, id_archivo):
    """Muestra la tarjeta de información y metadatos de un archivo seleccionado.

    Verifica la existencia del curso contenedor y del archivo apuntado por los
    identificadores numéricos correspondientes. Recupera la información detallada
    del recurso para su posterior consumo o gestión.

    Args:
        id_curso (int): Identificador del curso al que pertenece el archivo.
        id_archivo (int): Clave primaria del archivo solicitado.

    Returns:
        Response: Plantilla HTML 'detalle_archivo.html' procesada con el contexto
            del archivo y permisos de rol si los recursos son válidos; de lo
            contrario, redirige a las vistas generales con alertas flash de error.
    """
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    curso_actual = obtener_curso_por_id(id_curso)

    if not curso_actual:
        flash('Curso no existe', 'error')
        return redirect(url_for('visualizar_curso.visualizar_cursos'))

    archivo = obtener_por_id(id_archivo)
    if not archivo:
        flash('Archivo no existe', 'error')
        return redirect(url_for('visualizar_archivo.visualizar_archivos', id_curso=id_curso))

    rol = session.get('rol')

    return render_template(
        'detalle_archivo.html',
        archivo=archivo,
        curso=curso_actual,
        rol=rol
    )

@visualizarArchivo_bp.route('/archivo/ver/<int:id_archivo>')
def ver_archivo(id_archivo):
    """Transmite y renderiza un archivo almacenado en disco hacia el navegador.

    Recupera la ruta física absoluta de almacenamiento indexada en el registro
    del archivo y utiliza la infraestructura de Flask para enviar el binario,
    permitiendo su lectura en línea en el navegador web sin forzar la descarga.

    Args:
        id_archivo (int): Clave primaria del archivo que se desea abrir.

    Returns:
        Response: Flujo binario enviado mediante `send_file` con la bandera de
            adjunto deshabilitada (`as_attachment=False`), o redirección al
            catálogo general si el archivo no se localiza en el sistema.
    """
    if 'id_usuario' not in session:
        return redirect(url_for('auth.login'))

    archivo = obtener_por_id(id_archivo)

    if not archivo:
        flash('Archivo no encontrado', 'error')
        return redirect(url_for('visualizar_curso.visualizar_cursos'))

    return send_file(
        archivo['ruta'],
        as_attachment=False
    )