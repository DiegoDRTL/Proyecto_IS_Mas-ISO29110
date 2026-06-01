"""Módulo de esquemas de validación de datos para la gestión de usuarios.

Este módulo define las estructuras de datos y reglas de negocio necesarias
para validar la información de los usuarios durante el proceso de registro
dentro del sistema mediante el uso de Pydantic.
"""

from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
from datetime import date


class User_form(BaseModel):
    """Esquema de validación para los datos recolectados del formulario de registro.

    Aplica restricciones de tipos, formatos específicos (como correos y fechas)
    y validaciones complejas de interdependencia de campos para asegurar la
    integridad de los datos de un nuevo usuario antes de persistirlos.

    Atributos:
        nombre (str): Nombre(s) de pila del usuario.
        apellido_paterno (str): Primer apellido del usuario.
        apellido_materno (str | None): Segundo apellido del usuario. Es opcional
            y por defecto se asigna como None si se recibe vacío.
        contrasena (str): Contraseña elegida por el usuario (mínimo 6 caracteres
            y al menos un número).
        confirmar_contrasena (str): Duplicado de la contraseña para validación de
            coincidencia.
        fecha_nacimiento (date): Fecha de nacimiento del usuario, parseada
            automáticamente desde formatos válidos como ISO 8601 ('YYYY-MM-DD').
        correo (EmailStr): Dirección de correo electrónico válida.
        telefono (str): Número telefónico de contacto del usuario.
    """

    nombre: str
    apellido_paterno: str
    apellido_materno: str | None = None
    contrasena: str
    confirmar_contrasena: str
    fecha_nacimiento: date
    correo: EmailStr
    telefono: str

    @field_validator('apellido_materno', mode='before')
    @classmethod
    def transformar_vacios_a_none(cls, value: str) -> str | None:
        """Preprocesa el apellido materno para normalizar cadenas vacías.

        Intercepta el valor enviado por el navegador web antes de la validación
        estricta de Pydantic. Si detecta que el campo llegó vacío o solo con
        espacios, lo transforma en `None`.

        Args:
            value (str): Cadena de texto cruda extraída del formulario web.

        Returns:
            str | None: None si la cadena original estaba vacía, o el texto
                original intacto en caso contrario.
        """
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator('confirmar_contrasena')
    @classmethod
    def confirm_pswd_validator(cls, value: str, info: ValidationInfo) -> str:
        """Valida la concordancia e igualdad entre los dos campos de contraseña.

        Compara el campo de confirmación actual contra los datos ya procesados
        dentro del flujo del modelo para el campo principal de la contraseña.

        Args:
            value (str): Texto ingresado en el campo de confirmación de contraseña.
            info (ValidationInfo): Objeto de contexto de Pydantic que contiene los
                atributos previamente validados en el ciclo actual.

        Returns:
            str: El valor de confirmación validado si coincide con la contraseña.

        Raises:
            ValueError: Si la contraseña de confirmación no es idéntica a la
                original registrada en el diccionario de datos del contexto.
        """
        if 'contrasena' in info.data and value != info.data['contrasena']:
            raise ValueError('Las contraseñas no coinciden')
        return value

    @field_validator('contrasena')
    @classmethod
    def password_fuerte(cls, value: str) -> str:
        """Evalúa los criterios mínimos de seguridad de la contraseña del usuario.

        Comprueba que la cadena cumpla con una longitud segura y que incluya una
        combinación de caracteres alfanuméricos mediante la presencia de dígitos.

        Args:
            value (str): Contraseña en texto plano ingresada en el formulario.

        Returns:
            str: La contraseña evaluada y aprobada.

        Raises:
            ValueError: Si la longitud es inferior a 6 caracteres o si carece
                de al menos un número.
        """
        if len(value) < 6:
            raise ValueError('La contraseña debe tener un mínimo de 6 caracteres')
        if not any(char.isdigit() for char in value):
            raise ValueError('La contraseña debe de incluir al menos un número')
        return value