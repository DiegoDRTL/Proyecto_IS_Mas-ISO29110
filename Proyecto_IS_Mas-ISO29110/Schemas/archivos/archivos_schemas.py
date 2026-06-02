"""Módulo de gestión y persistencia de archivos multimedia en el sistema.

Este módulo provee la clase `ArchivoModelo`, encargada de encapsular las reglas de
negocio para la validación de extensiones de archivos, el almacenamiento físico
en el servidor web de Flask y el registro de metadatos en la base de datos
relacional del sistema.
"""

import os
from datetime import datetime
from werkzeug.utils import secure_filename

from alchemyClasses.archivo import create_archivo

class ArchivoModelo:
    """Clase controladora para la validación y almacenamiento de archivos de cursos.

    Atributos:
        EXTENSIONES_PERMITIDAS (set): Colección de cadenas de texto con los formatos
            de archivos que el sistema considera seguros y válidos para subir.
        ruta_almacenamiento (str): Directorio físico en el servidor donde se
            guardarán permanentemente los archivos subidos.
    """

    EXTENSIONES_PERMITIDAS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

    def __init__(self, ruta_almacenamiento):
        """Inicializa una nueva instancia del administrador de archivos.

        Args:
            ruta_almacenamiento (str): Ruta del directorio destino para el volcado
                de los archivos multimedia del sistema.
        """
        self.ruta_almacenamiento = ruta_almacenamiento

    def extension_valida(self, nombre_archivo):
        """Determina si un archivo cuenta con una extensión de formato permitida.

        Verifica la presencia de un punto divisorio en la cadena del nombre y extrae
        los caracteres posteriores para compararlos contra el set de extensiones
        válidas del sistema.

        Args:
            nombre_archivo (str): Nombre completo del archivo enviado por el usuario
                (incluyendo su formato de extensión).

        Returns:
            bool: True si el archivo termina con un formato aprobado por el sistema,
                False en caso contrario.
        """
        return '.' in nombre_archivo and \
            nombre_archivo.rsplit('.', 1)[1].lower() in self.EXTENSIONES_PERMITIDAS

    def guardar_y_registrar(self, archivo_flask, id_curso_sd):
        """Procesa, guarda físicamente en disco y registra en la base de datos un archivo.

        El método valida la existencia del objeto, comprueba la extensión de forma
        preventiva, sanitiza el nombre de archivo original para prevenir vulnerabilidades
        de directorios cruzados, guarda el binario en la ruta configurada y delega
        la persistencia de sus metadatos a las clases de alquimia.

        Args:
            archivo_flask (FileStorage): Objeto FileStorage nativo de Flask que
                contiene el flujo binario e información del archivo subido.
            id_curso_sd (int): Identificador único del curso al cual quedará vinculado
                el archivo en la base de datos.

        Returns:
            tuple: Un par ordenado (bool, str) donde el primer elemento indica el
                estado de éxito de toda la operación y el segundo elemento provee
                un mensaje detallado del resultado o del error atrapado.
        """
        if not archivo_flask or archivo_flask.filename == '':
            return False, "No se selecciono un archivo"
        if not self.extension_valida(archivo_flask.filename):
            return False, "Formato no permitido. Solo PDF, DOC, JPG o PNG"

        nombre_original = secure_filename(archivo_flask.filename)
        extension = nombre_original.rsplit('.', 1)[1].lower()
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        ruta_completa = os.path.join(self.ruta_almacenamiento, nombre_original)

        try:
            archivo_flask.save(ruta_completa) # guardado del archivo

            registro_exitoso = create_archivo(
                nombre = nombre_original,
                tipo_extension = extension,
                fecha_subida = fecha_actual,
                ruta = ruta_completa,
                id_curso= id_curso_sd
            )

            if registro_exitoso:
                return True, f"Guardado con exito y guardado en BD con fecha {fecha_actual}"

            else:
                return False, "No se pudo registrar en la BD"
        except Exception as e:
            return False, f"Error al procesar el archivo: {str(e)}"