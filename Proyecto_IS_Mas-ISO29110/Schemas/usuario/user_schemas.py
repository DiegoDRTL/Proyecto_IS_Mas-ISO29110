from pydantic import BaseModel, EmailStr, Field, field_validator

class User_form(BaseModel):
    # Validaciones para los datos ingresados en el formulario del usuario
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    correo: EmailStr = Field(..., description="Correo de usuario")
    password: str = Field(..., min_length=8, description="Contrasena de al menos 8 caracteres")

    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def confirm_pswd_validator(cls, v, info):
        """
        'v' contrasena guardada en confirm_password
        'info.data' contiene todos los datos del formulario, incluyendo la contrasena guardada en 'password'
         - Se compara 'v' con 'info.data['password']' para verificar que ambas contrasenas coincidan
         - Si no coinciden, se lanza un error de validacion indicando que las contrasenas no coinciden
         - Si coinciden, se retorna 'v', lo que permite que la validacion continue sin problemas
        """
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

    @field_validator('password')
    @classmethod
    def password_fuerte(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe de incluir al menos un número')
        return v