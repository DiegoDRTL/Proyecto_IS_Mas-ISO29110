USE proyecto;

-- Tabla Usuario (id, nombre, correo, contrasena, rol)
CREATE TABLE Usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(250) NOT NULL,
    rol VARCHAR(50) NOT NULL
);

-- Tabla Profesor (id, nombre, rfc, especialidad)
CREATE TABLE Profesor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rfc VARCHAR(13) NOT NULL UNIQUE,
    especialidad VARCHAR(100)
);

-- Tabla Session (sessionId, status, userId)
CREATE TABLE Session (
    sessionId INT AUTO_INCREMENT PRIMARY KEY,
    status BOOLEAN NOT NULL,
    userId INT NOT NULL,
    CONSTRAINT fk_session_usuario
        FOREIGN KEY (userId) REFERENCES Usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Tabla Curso (idCurso, titulo, descripcion, datosAcademicos, estado, idProfesor)
CREATE TABLE Curso (
    idCurso INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    datosAcademicos TEXT,
    estado VARCHAR(50),
    idProfesor INT NOT NULL,
    CONSTRAINT fk_curso_profesor
        FOREIGN KEY (idProfesor) REFERENCES Profesor(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Tabla Archivo (idArchivo,nombre, tipoExtension, fechaSubida, idCurso)
CREATE TABLE Archivo (
    idArchivo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipoExtension VARCHAR(10),
    fechaSubida DATE,
    idCurso INT NOT NULL,
    CONSTRAINT fk_archivo_curso
        FOREIGN KEY (idCurso) REFERENCES Curso(idCurso)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Tabla Enrollment (Relación entre Usuario y Curso)
CREATE TABLE Enrollment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userId INT NOT NULL,
    courseId INT NOT NULL,
    CONSTRAINT fk_enrollment_user
        FOREIGN KEY (userId) REFERENCES Usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_enrollment_course
        FOREIGN KEY (courseId) REFERENCES Curso(idCurso)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);