from pydantic import BaseModel, Field, field_validator

class Curso_form(BaseModel):
    """
    Validaciones para los datos ingresados en el formulario de creación de curso.

    Atributos:
        nombre (str): Nombre o título del curso (5-100 caracteres).
        capacidad (int): Capacidad máxima de alumnos (debe ser mayor a 0).
        estado (str): Estado inicial del curso ('Abierto' o 'Cerrado').
        descripcion (str): Descripción detallada del curso (10-500 caracteres).
    """
    nombre: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Nombre o título del curso"
    )

    capacidad: int = Field(
        ...,
        gt=0,
        description="Capacidad máxima de alumnos para el curso"
    )

    estado: str = Field(
        ...,
        description="Estado inicial del curso"
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
        """Valida que el nombre no esté vacío y elimina espacios en blanco extremos."""
        if not v or not v.strip():
            raise ValueError('El nombre del curso no puede estar vacío.')
        return v.strip()

    @field_validator('estado')
    @classmethod
    def estado_validator(cls, v: str) -> str:
        """Garantiza que el estado sea estrictamente 'Abierto' o 'Cerrado'."""
        if v not in ['Abierto', 'Cerrado']:
            raise ValueError('El estado debe ser "Abierto" o "Cerrado".')
        return v

    @field_validator('descripcion')
    @classmethod
    def descripcion_validator(cls, v: str) -> str:
        """Valida que la descripción no esté vacía y limpia espacios innecesarios."""
        if not v or not v.strip():
            raise ValueError('La descripción del curso no puede estar vacía.')
        return v.strip()