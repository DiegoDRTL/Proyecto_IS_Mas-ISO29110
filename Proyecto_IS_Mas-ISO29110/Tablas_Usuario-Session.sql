CREATE TABLE Usuario(
	id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR (100) NOT NULL UNIQUE,
    contrasena VARCHAR(250) NOT NULL, 
    rol ENUM('alumno', 'administrador', 'profesor')

);

CREATE TABLE Sesion(
	id_sesion VARCHAR(128) PRIMARY KEY, 
    estado BOOLEAN NOT NULL, 
    id_usuario INT NOT NULL,
	FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);