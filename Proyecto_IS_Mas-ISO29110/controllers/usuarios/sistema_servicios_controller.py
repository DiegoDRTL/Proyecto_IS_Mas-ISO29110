import os
import subprocess
from datetime import datetime
from flask import send_file, flash, redirect, url_for
from alchemyClasses.usuario import obtener_logs_auditoria as db_logs

def obtener_logs_auditoria():
    """Retorna la lista de acciones simuladas para la auditoría del sistema."""
    return db_logs()

def ejecutar_respaldo_database():
    """Genera el dump SQL de la base de datos y lo prepara para descarga."""
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
        return redirect(url_for('admin_sistema.ver_logs')) # Ajustado al blueprint actual