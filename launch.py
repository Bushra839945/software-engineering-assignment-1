"""Beginner-friendly launcher. Run after installing requirements.txt."""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script):
    subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)


def main():
    print("Assignment 1 - Choose a task")
    print("1. Student management (opens the web interface)")
    print("2. Text API with three consumer keys")
    print("3. Employee API with login and roles")
    choice = input("Enter 1, 2 or 3: ").strip()
    if choice == "1":
        backend = subprocess.Popen([sys.executable, str(ROOT / "task1_students/app.py")], cwd=ROOT)
        try:
            time.sleep(1)
            if backend.poll() is not None:
                raise SystemExit("The API could not start. Check whether port 5001 is already in use.")
            print("Open http://localhost:8501 if a browser does not open automatically.")
            subprocess.run([sys.executable, "-m", "streamlit", "run",
                            str(ROOT / "task1_students/streamlit_app.py"),
                            "--server.address=127.0.0.1", "--browser.gatherUsageStats=false"], cwd=ROOT)
        finally:
            backend.terminate()
            try:
                backend.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend.kill()
    elif choice == "2":
        if not (ROOT / "task2_api_keys/api_keys.json").exists():
            run("task2_api_keys/generate_keys.py")
        print("The API runs at http://127.0.0.1:5002. Use cURL in a second terminal.")
        run("task2_api_keys/app.py")
    elif choice == "3":
        run("task3_auth/setup_users.py")
        print("The API runs at http://127.0.0.1:5003. Use cURL in a second terminal.")
        run("task3_auth/app.py")
    else:
        print("Please run the launcher again and enter 1, 2 or 3.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
    except subprocess.CalledProcessError:
        raise SystemExit("A task stopped with an error. Read the message above.")
