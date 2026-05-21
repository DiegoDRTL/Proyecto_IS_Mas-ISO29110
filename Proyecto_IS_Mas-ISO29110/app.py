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
from controllers.archivos.eliminar_controller import eliminarArchivo_bp # Eliminar archivos subidos
from controllers.cursos.inscribir_controller import inscribir_bp # Inscribirse a cursos disponibles


app = Flask(__name__)
app.secret_key = 'clave_secreta_curso_2024'

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(registrarUsuario_bp)
app.register_blueprint(create_bp)
app.register_blueprint(profesor_bp)
app.register_blueprint(visualizarArchivo_bp)
app.register_blueprint(visualizarCurso_bp)
app.register_blueprint(crearCurso_bp)
app.register_blueprint(eliminar_curso_bp)
app.register_blueprint(eliminarArchivo_bp)
app.register_blueprint(inscribir_bp)



if __name__ == '__main__':
    app.run(debug=True)