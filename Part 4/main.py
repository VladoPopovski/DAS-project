import multiprocessing
import os
import signal
from app.flask_app_singleton import FlaskAppSingleton
from visualization.visualization import run_dash_server

class ProcessManager:
    """
    Handles the initialization and management of Flask and Dash processes.
    """

    def __init__(self):
        self.flask_process = None
        self.dash_process = None

    def run_flask(self):
        """
        Function to start the Flask API.
        """
        try:
            flask_app = FlaskAppSingleton().get_app()
            flask_app.run(debug=True, port=5000, use_reloader=False)
        except Exception as e:
            print(f"Flask API process encountered an error: {e}")

    def run_dash(self):
        """
        Function to start the Dash Visualizer.
        """
        try:
            run_dash_server()
        except Exception as e:
            print(f"Dash process encountered an error: {e}")

    def terminate_processes(self, signum, frame):
        """
        Terminate both Flask and Dash processes gracefully.
        """
        print("Terminating all processes...")
        if self.flask_process.is_alive():
            self.flask_process.terminate()
            self.flask_process.join()
        if self.dash_process.is_alive():
            self.dash_process.terminate()
            self.dash_process.join()
        print("All processes terminated.")

    def start(self):
        """
        Start both Flask and Dash processes and handle termination signals.
        """
        multiprocessing.set_start_method("spawn")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        # Initialize the processes
        self.flask_process = multiprocessing.Process(target=self.run_flask)
        self.dash_process = multiprocessing.Process(target=self.run_dash)

        # Set up signal handlers for termination
        signal.signal(signal.SIGINT, self.terminate_processes)
        signal.signal(signal.SIGTERM, self.terminate_processes)

        print("Starting Flask API process...")
        self.flask_process.start()
        print("Starting Dash Visualizer process...")
        self.dash_process.start()

        # Wait for the processes to finish
        self.flask_process.join()
        self.dash_process.join()


if __name__ == "__main__":
    manager = ProcessManager()
    manager.start()
