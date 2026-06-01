"""Módulo de validación de esquemas de datos para la gestión de cursos.

Este módulo define la clase `Curso_form` apoyándose en el framework Pydantic
para asegurar la integridad y el correcto tipado de los datos capturados en
el formulario de creación y edición de cursos de idiomas.
"""

from pydantic import BaseModel, Field, field_validator


class Curso_form(BaseModel):
    """Esquema de validación para los datos del formulario de creación de curso.

    Define las restricciones de longitud, tipos de datos y limpiezas iniciales
    para los campos recolectados desde la interfaz web antes de permitir su
    procesamiento en el controlador.

    Atributos:
        nombre (str): Nombre o título del curso (5-100 caracteres).
        capacidad (int): Capacidad máxima de alumnos admitidos (debe ser mayor a 0).
        estado (str): Estado operativo inicial del curso ('Abierto' o 'Cerrado').
        descripcion (str): Resumen y objetivos del curso (10-500 caracteres).
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
        """Valida la integridad del nombre del curso y sanitiza sus espacios.

        Remueve los espacios en blanco sobrantes en los extremos de la cadena y
        previene que el campo contenga únicamente caracteres invisibles.

        Args:
            v (str): El valor alfanumérico crudo del nombre ingresado en el input.

        Returns:
            str: La cadena de texto sanitizada sin espacios excedentes en los extremos.

        Raises:
            ValueError: Si la cadena resultante está completamente vacía.
        """
        if not v or not v.strip():
            raise ValueError('El nombre del curso no puede estar vacío.')
        return v.strip()

    @field_validator('estado')
    @classmethod
    def estado_validator(cls, v: str) -> str:
        """Garantiza que el estado asignado corresponda a una opción permitida.

        Evalúa que la cadena recibida coincida estrictamente con los estados lógicos
        de negocio establecidos para el ciclo de vida de un curso.

        Args:
            v (str): El estado del curso enviado desde el formulario.

        Returns:
            str: El mismo estado validado sin alteraciones.

        Raises:
            ValueError: Si el estado no equivale exactamente a 'Abierto' o 'Cerrado'.
        """
        if v not in ['Abierto', 'Cerrado']:
            raise ValueError('El estado debe ser "Abierto" o "Cerrado".')
        return v

    @field_validator('descripcion')
    @classmethod
    def descripcion_validator(cls, v: str) -> str:
        """Valida la integridad de la descripción del curso y sanitiza sus espacios.

        Verifica que el contenido no conste únicamente de espacios en blanco y
        limpia los extremos de la cadena para asegurar un almacenamiento prolijo.

        Args:
            v (str): El bloque de texto crudo de la descripción.

        Returns:
            str: El texto de la descripción sanitizado.

        Raises:
            ValueError: Si la descripción evaluada se encuentra vacía.
        """
        if not v or not v.strip():
            raise ValueError('La descripción del curso no puede estar vacía.')
        return v.strip()