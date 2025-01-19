import multiprocessing
import os
import signal
import requests
from app.flask_app_singleton import FlaskAppSingleton

DATA_FOLDER = "/app/data"


class ProcessManager:
    """
    Handles the initialization and management of Flask and Dash processes.
    """

    def __init__(self):
        self.flask_process = None
        self.dash_service_url = "http://visualization_service:8050"

    def run_flask(self):
        """
        Function to start the Flask API.
        """
        try:
            flask_app = FlaskAppSingleton().get_app()
            self.add_routes(flask_app)
            flask_app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
        except Exception as e:
            print(f"Flask API process encountered an error: {e}")

    def add_routes(self, app):
        """
        Function to add routes to Flask API.
        """
        from api import get_data
        app.add_url_rule('/api/data/<issuer_code>', view_func=get_data)

    def start_dash(self):
        """
        Function to trigger the Dash visualization service via API.
        """
        try:
            response = requests.get(self.dash_service_url)
            if response.status_code == 200:
                print("Dash Visualization Service is running!")
            else:
                print(f"Dash service not responding. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error contacting Dash Visualization Service: {e}")

    def terminate_processes(self, signum, frame):
        """
        Terminate the Flask process gracefully.
        """
        print("Terminating all processes...")
        if self.flask_process and self.flask_process.is_alive():
            self.flask_process.terminate()
            self.flask_process.join()
        print("All processes terminated.")

    def start(self):
        """
        Start Flask API and check Dash service.
        """
        multiprocessing.set_start_method("spawn")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        # Initialize Flask process
        self.flask_process = multiprocessing.Process(target=self.run_flask)

        # Set up signal handlers for termination
        signal.signal(signal.SIGINT, self.terminate_processes)
        signal.signal(signal.SIGTERM, self.terminate_processes)

        print("🚀 Starting Flask API process...")
        self.flask_process.start()

        print("🔍 Checking Dash Visualization Service...")
        self.start_dash()

        self.flask_process.join()


if __name__ == "__main__":
    manager = ProcessManager()
    manager.start()
