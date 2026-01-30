"""
Запуск сервера блока A
"""

from flask import Flask
from api.routes import bp as partners_bp
from api.admin_routes import bp as admin_bp
from config import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.api.secret_key

# Регистрируем Blueprints
app.register_blueprint(partners_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return {'message': 'Block A: Partners DB API', 'version': '1.0.0'}

if __name__ == '__main__':
    app.run(
        host=config.api.host,
        port=config.api.port,
        debug=config.api.debug
    )
