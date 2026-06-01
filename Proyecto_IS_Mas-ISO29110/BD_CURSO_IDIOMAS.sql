DROP DATABASE IF EXISTS BD_CURSO_IDIOMAS;
CREATE DATABASE BD_CURSO_IDIOMAS;
USE BD_CURSO_IDIOMAS;

-- =====================
-- USUARIO (tabla padre)
-- =====================
CREATE TABLE USUARIO (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    apellido_paterno VARCHAR(50),
    apellido_materno VARCHAR(50),
    contraseña VARCHAR(100),
    fecha_nacimiento DATE,
    rol VARCHAR(30) NOT NULL, -- Se mantiene VARCHAR para permitir flexibilidad en los roles
    correo VARCHAR(100) UNIQUE,
    telefono VARCHAR(20)
);

-- =====================
-- SUBTIPOS
-- =====================
CREATE TABLE PROFESOR (
    id_usuario INT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE ALUMNO (
    id_usuario INT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE ADMINISTRADOR (
    id_usuario INT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================
-- SESION (1:1)
-- =====================
CREATE TABLE SESION (
    id_usuario INT PRIMARY KEY,
    status VARCHAR(255),
    ultima_conexion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================
-- CURSO (1:N con PROFESOR)
-- =====================
CREATE TABLE CURSO (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    estado VARCHAR(20),
    nombre VARCHAR(100),
    capacidad INT,
    descripcion VARCHAR(500),
    FOREIGN KEY (id_usuario) REFERENCES PROFESOR(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================
-- ARCHIVO
-- =====================
CREATE TABLE ARCHIVO (
    id_archivo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    tipo_extension VARCHAR(10),
    fecha_subida DATE,
    ruta VARCHAR(1000)
);

-- =====================
-- N:M CURSO-ARCHIVO
-- =====================
CREATE TABLE CURSO_ARCHIVO (
    id_curso INT,
    id_archivo INT,
    PRIMARY KEY (id_curso, id_archivo),
    FOREIGN KEY (id_curso) REFERENCES CURSO(id_curso),
    FOREIGN KEY (id_archivo) REFERENCES ARCHIVO(id_archivo)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================
-- N:M ALUMNO-CURSO
-- =====================
CREATE TABLE INSCRIBE (
    id_usuario INT,
    id_curso INT,
    PRIMARY KEY (id_usuario, id_curso),
    FOREIGN KEY (id_usuario) REFERENCES ALUMNO(id_usuario),
    FOREIGN KEY (id_curso) REFERENCES CURSO(id_curso)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);