from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp

app = Flask(__name__)
app.secret_key = 'clave_secreta_curso_2024'

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True)