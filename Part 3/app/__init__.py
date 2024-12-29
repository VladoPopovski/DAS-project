from flask import Flask
from flask_cors import CORS



def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['UPLOAD_FOLDER'] = '../downloads'


    CORS(app)


    from app.routes import routes_blueprint
    app.register_blueprint(routes_blueprint)

    return app
