"""
Módulo de administración del sistema.

Este controlador proporciona herramientas administrativas como la
visualización de logs de auditoría y la generación de respaldos de la base
de datos.

Está restringido únicamente a usuarios con rol de administrador e incluye
funcionalidades críticas de mantenimiento del sistema.
"""

import os
import subprocess
from datetime import datetime
from flask import send_file, flash, redirect, url_for
from alchemyClasses.usuario import obtener_logs_auditoria as db_logs

def obtener_logs_auditoria():
    """Obtiene los registros de auditoría del sistema.

    Retorna la información de logs almacenados en el sistema de
    auditoría, los cuales representan las acciones realizadas por los
    usuarios dentro de la aplicación.

    Returns:
        Any: Lista o estructura de datos con los registros de auditoría
            obtenidos desde la base de datos o servicio correspondiente.
    """
    return db_logs()

def ejecutar_respaldo_database():
    """Genera un respaldo de la base de datos y lo envía como descarga.

    Construye un archivo de respaldo en formato SQL utilizando el comando
    `mysqldump`, lo guarda temporalmente en el sistema y posteriormente
    lo envía al usuario como archivo descargable. En caso de error,
    notifica la falla y redirige a la vista de administración del sistema.

    Returns:
        Response: Archivo SQL de respaldo descargable si la operación es
            exitosa, o redirección a la vista de administración en caso
            de error.
    """
    try:
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_BD_CURSO_IDIOMAS_{fecha_str}.sql"
        filepath = os.path.join("/tmp", filename)

        db_user = "root"
        db_password = "tu_password"
        db_name = "BD_CURSO_IDIOMAS"

        comando = f"mysqldump -u {db_user} -p{db_password} {db_name} > {filepath}"
        subprocess.run(comando, shell=True, check=True)

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        flash(f"Error al generar el respaldo de seguridad: {str(e)}", "error")
        return redirect(url_for('admin_sistema.ver_logs'))  # Ajustado al blueprint actual