-- =====================
-- USUARIO (tabla padre)
-- =====================
CREATE TABLE USUARIO (
  id_usuario INT PRIMARY KEY,
  nombre VARCHAR(50),
  apellido_paterno VARCHAR(50),
  apellido_materno VARCHAR(50),
  contraseña VARCHAR(100),
  fecha_nacimiento DATE
);

-- =====================
-- SUBTIPOS
-- =====================
CREATE TABLE PROFESOR (
  id_usuario INT PRIMARY KEY,
  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

CREATE TABLE ALUMNO (
  id_usuario INT PRIMARY KEY,
  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

CREATE TABLE ADMINISTRADOR (
  id_usuario INT PRIMARY KEY,
  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

-- =====================
-- MULTIVALUADOS
-- =====================
CREATE TABLE TELEFONO_USUARIO (
  id_usuario INT,
  telefono VARCHAR(20),
  PRIMARY KEY (id_usuario, telefono),
  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

CREATE TABLE CORREO_USUARIO (
  id_usuario INT,
  correo VARCHAR(100),
  PRIMARY KEY (id_usuario, correo),
  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

-- =====================
-- SESION (1:1)
-- =====================
CREATE TABLE SESION (
  id_usuario INT PRIMARY KEY,
  status VARCHAR(20),
  FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

-- =====================
-- CURSO (1:N con PROFESOR)
-- =====================
CREATE TABLE CURSO (
  id_curso INT PRIMARY KEY,
  id_usuario INT NOT NULL,
  estado VARCHAR(20),
  nombre VARCHAR(100),
  capacidad INT,
  FOREIGN KEY (id_usuario) REFERENCES PROFESOR(id_usuario)
);

-- =====================
-- ARCHIVO
-- =====================
CREATE TABLE ARCHIVO (
  id_archivo INT PRIMARY KEY,
  nombre VARCHAR(100),
  tipo_extension VARCHAR(10),
  fecha_subida DATE
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
);