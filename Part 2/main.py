import multiprocessing
import os
import signal
from app import create_app
from visualization.visualization import run_dash_server

def run_flask():
    """Функција за стартување на Flask API"""
    try:
        flask_app = create_app()
        flask_app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Flask API process encountered an error: {e}")

def run_dash():
    """Функција за стартување на Dash Visualizer"""
    try:
        run_dash_server()
    except Exception as e:
        print(f"Dash process encountered an error: {e}")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    flask_process = multiprocessing.Process(target=run_flask)
    dash_process = multiprocessing.Process(target=run_dash)

    def terminate_processes(signum, frame):
        print("Terminating all processes...")
        flask_process.terminate()
        dash_process.terminate()
        flask_process.join()
        dash_process.join()
        print("All processes terminated.")

    signal.signal(signal.SIGINT, terminate_processes)
    signal.signal(signal.SIGTERM, terminate_processes)

    print("Starting Flask API process...")
    flask_process.start()
    print("Starting Dash Visualizer process...")
    dash_process.start()


    flask_process.join()
    dash_process.join()
