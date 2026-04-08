CREATE TABLE Curso (
    idCurso VARCHAR(50) PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    datosAcademicos TEXT,
    estado VARCHAR(50),
    profesorId INT NOT NULL
    
    FOREIGN KEY (profesorId) REFERENCES Profesor(id)
);

CREATE TABLE Archivo (
    idArchivo VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipoExtension VARCHAR(10),
    fechaSubida DATE,
    size FLOAT,
    idCurso VARCHAR(50) NOT NULL,
    
    CONSTRAINT fk_archivo_curso
    FOREIGN KEY (idCurso) REFERENCES Curso(idCurso)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);