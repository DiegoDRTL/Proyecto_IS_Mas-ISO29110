INSERT INTO Usuario (id_usuario, nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento) VALUES ('100087', 'Diego', 'Tapia', 'Linares', 'seguro1653##', '2005-08-20');
INSERT INTO Usuario (id_usuario, nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento) VALUES ('100512', 'Isabel', 'Aguilar', 'García', 'perrofav54$', '2005-03-12');
INSERT INTO Usuario (id_usuario, nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento) VALUES ('000542', 'Mayra', 'Escobar', 'Santander', 'dominio431&', '2005-12-08');
INSERT INTO Usuario (id_usuario, nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento) VALUES ('287536', 'Pablo', 'Martínez', 'Huerta', 'abuela64#', '2005-04-30');
INSERT INTO Usuario (id_usuario, nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento) VALUES ('087638', 'Francisco', 'Valdés', 'Souto', 'clases29110$', '1993-10-29');
INSERT INTO Usuario (id_usuario, nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento) VALUES ('187253', 'Valeria', 'García', 'Landa', 'BasDat86#', '2000-02-16');
INSERT INTO Usuario (id_usuario, nombre, apellido_paterno, apellido_materno, contraseña, fecha_nacimiento) VALUES ('098036', 'Fernando', 'Fong', 'Baeza', 'Secretos2003&', '2001-11-15');

INSERT INTO ADMINISTRADOR (id_usuario) VALUES ('100087');
INSERT INTO ADMINISTRADOR (id_usuario) VALUES ('100512');
INSERT INTO ADMINISTRADOR (id_usuario) VALUES ('000542');
INSERT INTO ADMINISTRADOR (id_usuario) VALUES ('287536');

INSERT INTO PROFESOR (id_usuario) VALUES ('087638');

INSERT INTO ALUMNO (id_usuario) VALUES ('187253');
INSERT INTO ALUMNO (id_usuario) VALUES ('098036');

INSERT INTO TELEFONO_USUARIO (id_usuario, telefono) VALUES ('100087', '5682735480');

INSERT INTO CORREO_USUARIO (id_usuario, correo) VALUES ('100087', 'diegodrtl@ciencias.unam.mx');
