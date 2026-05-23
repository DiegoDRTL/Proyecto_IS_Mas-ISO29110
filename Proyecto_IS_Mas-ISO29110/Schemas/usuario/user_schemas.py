from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
from datetime import date

class User_form(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    contrasena: str
    confirmar_contrasena: str
    fecha_nacimiento: date  # Pydantic parseará los strings 'YYYY-MM-DD' automáticamente
    correo: EmailStr        # Valida que sea un correo real
    telefono: str

    @field_validator('confirmar_contrasena')
    @classmethod
    def confirm_pswd_validator(cls, value: str, info: ValidationInfo) -> str:
        """
        'value' contiene lo que se escribió en confirmar_contrasena.
        'info.data' contiene todos los datos ya procesados del formulario, como 'contrasena'.
        """
        # Cambiado 'password' por 'contrasena'
        if 'contrasena' in info.data and value != info.data['contrasena']:
            raise ValueError('Las contraseñas no coinciden')
        return value

    @field_validator('contrasena')
    @classmethod
    def password_fuerte(cls, value: str) -> str:
        """
        Valida que la contraseña tenga al menos un número.
        """
        if not any(char.isdigit() for char in value):
            raise ValueError('La contraseña debe de incluir al menos un número')
        return value