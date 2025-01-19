from flask import Flask
from flask_cors import CORS
from .routes import routes_blueprint
 # Импортирај го Blueprint-от

class FlaskAppSingleton:
    """
    Singleton class to ensure only one instance of the Flask application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.app = cls._create_app()  # Пополнување на cls._instance.app
        return cls._instance

    @staticmethod
    def _create_app():
        """
        Factory method to create and configure the Flask application instance.
        """
        app = Flask(__name__)  # Создавање на Flask инстанца

        # Configure application settings
        app.config['SECRET_KEY'] = 'your_secret_key'
        app.config['UPLOAD_FOLDER'] = '../downloads'

        # Enable Cross-Origin Resource Sharing (CORS)
        CORS(app)

        # Register blueprints for modular routing
        app.register_blueprint(routes_blueprint)  # РЕГИСТРАЦИЈА НА ROUTES

        return app

    def get_app(self):
        """
        Get the singleton instance of the Flask application.

        Returns:
            Flask: The Flask application instance.
        """
        return self._instance.app
