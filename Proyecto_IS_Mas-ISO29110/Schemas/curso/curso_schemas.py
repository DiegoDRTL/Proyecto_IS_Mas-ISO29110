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

    # 🌟 NUEVA ADICIÓN: Campo obligatorio para la capacidad de alumnos
    capacidad: int = Field(
        ...,
        gt=0, # Valida que sea estrictamente mayor a 0 alumnos
        description="Capacidad máxima de alumnos para el curso"
    )

    # 🌟 NUEVA ADICIÓN: Campo obligatorio para el estado (Abierto / Cerrado)
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
        if not v or not v.strip():
            raise ValueError('El nombre del curso no puede estar vacío.')
        return v.strip()

    # 🌟 NUEVA ADICIÓN: Validador para asegurar un estado consistente
    @field_validator('estado')
    @classmethod
    def estado_validator(cls, v: str) -> str:
        if v not in ['Abierto', 'Cerrado']:
            raise ValueError('El estado debe ser "Abierto" o "Cerrado".')
        return v

    @field_validator('descripcion')
    @classmethod
    def descripcion_validator(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('La descripción del curso no puede estar vacía.')
        return v.strip()