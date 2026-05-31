from flask import Flask
from controllers.usuarios.auth_controller import auth_bp # iniciar y cerrar sesion
from controllers.usuarios.dashboard_controller import dashboard_bp # tipo de usuario
from controllers.usuarios.register_controller import registrarUsuario_bp # Registrar usuario
from controllers.usuarios.createUser_controller import create_bp #crear usuario
from controllers.usuarios.profesor_controller import profesor_bp # Eliminar profesor
from controllers.archivos.visualizar_controller import visualizarArchivo_bp # Visualizar archivos subidos
from controllers.cursos.visualizar_controller import visualizarCurso_bp # Visualizar cursos disponibles
from controllers.cursos.crear_controller import crearCurso_bp # Crear cursos
from controllers.cursos.eliminar_controller import eliminar_curso_bp #eliminar curso
from controllers.archivos.subir_controller import subirArchivo_bp # Subir archivos
from controllers.archivos.eliminar_controller import eliminarArchivo_bp # Eliminar archivos subidos
from controllers.cursos.inscribir_controller import inscribir_bp # Inscribirse a cursos disponibles
from controllers.cursos.reportes_cursos_controller import reportes_cursos_bp #Visualiza reportes de cursos para el dashboard de administrador 
from controllers.usuarios.gestionar_usuarios_controller import gestionar_usuarios_bp #Gestion de usuarios por parte del administrador 
from controllers.usuarios.admin_sistema_controller import admin_sistema_bp # Configuracion del sistema y logs de auditoria para el administrador
app = Flask(__name__)
app.secret_key = 'clave_secreta_curso_2024'

# Configuracion global del tamano maximo de archivos (16mb)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 1. Autenticación y Usuarios
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(registrarUsuario_bp)
app.register_blueprint(create_bp)
app.register_blueprint(profesor_bp)
app.register_blueprint(gestionar_usuarios_bp)
app.register_blueprint(admin_sistema_bp)

# 2. Gestión de Archivos
app.register_blueprint(subirArchivo_bp)
app.register_blueprint(visualizarArchivo_bp)
app.register_blueprint(eliminarArchivo_bp)

# 3. Gestión de Cursos
app.register_blueprint(visualizarCurso_bp)
app.register_blueprint(eliminar_curso_bp, name='eliminar_curso')
app.register_blueprint(inscribir_bp, name='inscribir_curso')
app.register_blueprint(crearCurso_bp, name='curso')
app.register_blueprint(reportes_cursos_bp)


if __name__ == '__main__':
    app.run(debug=True)