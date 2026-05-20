from pydantic import BaseModel, Field, field_validator

class Curso_form(BaseModel):
    """
    Validaciones para los datos ingresados en el formulario de creación de curso.
    """
    nombre: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Nombre o título del curso"
    )
    descripcion: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Descripción detallada de los objetivos y contenido del curso"
    )

    @field_validator('nombre')
    @classmethod
    def nombre_validator(cls, v: str) -> str:
        """
        Valida que el nombre no sea solo espacios en blanco y
        remueve los espacios vacíos innecesarios al inicio y al final.
        """
        if not v or not v.strip():
            raise ValueError('El nombre del curso no puede estar vacío.')
        return v.strip()

    @field_validator('descripcion')
    @classmethod
    def descripcion_validator(cls, v: str) -> str:
        """
        Valida que la descripción cumpla con un formato limpio.
        """
        if not v or not v.strip():
            raise ValueError('La descripción del curso no puede estar vacía.')
        return v.strip()