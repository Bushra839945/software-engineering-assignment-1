# Assignment 1: Custom APIs and Microservices

CSC3109 Software Engineering, SZABIST University Larkana.

Three independent Python applications implement the assignment. Start with
**START_HERE.txt** for beginner instructions. No personal student identity has been
invented; add your name and registration number here if your instructor requires them.

| Folder | What it demonstrates | Address |
| --- | --- | --- |
| `task1_students` | Flask + SQLite CRUD and a Streamlit frontend | API `127.0.0.1:5001`; UI `localhost:8501` |
| `task2_api_keys` | Text processing with three consumer keys | API `127.0.0.1:5002` |
| `task3_auth` | Login, employee permissions and administrator CRUD | API `127.0.0.1:5003` |

Each task folder includes source code, a README, a cURL demonstration script,
`demo.mp4`, and `DEMONSTRATION.md`. These are local classroom applications.
The code has not been deployed to a public server.

## Setup

Tested with Python 3.12.14, Flask 3.1.3, Streamlit 1.66.1 and requests 2.34.2.
Install Python 3.12 from [python.org](https://www.python.org/downloads/).
SQLite support is already part of Python; no separate database installation is needed.

Windows: double-click `setup_windows.bat`, then `start_windows.bat`.
The equivalent commands, run from this folder, are:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe launch.py
```

macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python launch.py
```

Choose one task from the launcher. Leave its terminal open while testing.
Open a second terminal in this project folder for cURL demonstrations.
In the task READMEs, `python` means the Python interpreter in this environment:
`.\.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS/Linux.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

On macOS/Linux, replace the Python path with `.venv/bin/python`.
The tests create temporary databases and temporary credentials; your local records
are unaffected. The included validation run passed **40 automated tests**, including
a Streamlit UI test against a live Flask server. A real browser also exercised Task 1.
The cURL demonstrations checked 6 Task 1, 5 Task 2 and 15 Task 3 requests.

## Before submission

Read [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md). Publication, private key delivery
to the three assigned testers, and their own cURL testing remain to be completed
by the student. Do not treat the supplied sample videos as evidence of those people
testing the API. Add their sanitized evidence after they test.

## References

- [Flask quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [Streamlit rerun](https://docs.streamlit.io/develop/api-reference/execution-flow/st.rerun)
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [Python secrets](https://docs.python.org/3/library/secrets.html)

See EXPLAINED.md for the design and the difference between authentication and authorization.
