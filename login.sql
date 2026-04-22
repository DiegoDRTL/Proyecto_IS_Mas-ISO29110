DROP DATABASE IF EXISTS login; 
CREATE DATABASE login; 
USE login; 

CREATE TABLE Usuario(
	nombre_usuario VARCHAR(100) PRIMARY KEY, 
    contrasena VARCHAR(60) NOT NULL, 
    rol ENUM('usuario', 'administrador')
);
