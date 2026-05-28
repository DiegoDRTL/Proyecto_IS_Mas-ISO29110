import os
from datetime import datetime
from werkzeug.utils import secure_filename

from alchemyClasses.archivo import create_archivo

class ArchivoModelo:
    EXTENSIONES_PERMITIDAS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

    def __init__(self, ruta_almacenamiento):
        self.ruta_almacenamiento = ruta_almacenamiento

    def extension_valida(self, nombre_archivo):
        return '.' in nombre_archivo and \
            nombre_archivo.rsplit('.', 1)[1].lower() in self.EXTENSIONES_PERMITIDAS
    
    def guardar_y_registrar(self, archivo_flask, id_curso_sd):
        if not archivo_flask or archivo_flask.filename == '':
            return False, "No se selecciono un archivo"
        if not self.extension_valida(archivo_flask.filename):
            return False, "Formato no permitido. Solo PDF, DOC, JPG o PNG"
        
        nombre_original = secure_filename(archivo_flask.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        ruta_completa = os.path.join(self.ruta_almacenamiento, nombre_original)

        try:
            archivo_flask.save(ruta_completa) #guardado del archivo

            registro_exitoso = create_archivo(
                nombre = nombre_original,
                tipo_extension = extension,
                fecha_subida = fecha_actual,
                ruta = ruta_completa,
                id_curso= id_curso_sd
            )

            if registro_exitoso > 0:
                return True, f"Guardado con exito y guardado en BD con fecha {fecha_actual}"
            
            else:
                return False, f"Guardado con exito pero no se pudo subir a la BD"
        except Exception as e:
            return False, f"Error al procesar el archivo: {str(e)}"