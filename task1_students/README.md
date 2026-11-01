# Task 1: Students API and Streamlit

## Run

Use the root launcher and choose **1**. Or start these two commands in separate
terminals from the project root, using the virtual environment's Python:

```text
python task1_students/app.py
python -m streamlit run task1_students/streamlit_app.py
```

Visit `http://localhost:8501`. Flask runs at `http://127.0.0.1:5001`.
`students.db` is created automatically beside app.py. The table has `id`, `name`,
`department`, and `email`. The ID is automatically assigned, and email is unique.

## Endpoints

| Method | Path | Successful result |
| --- | --- | --- |
| GET | `/students` | 200: list of all students |
| GET | `/students/<id>` | 200: one student |
| POST | `/students` | 201: newly created student |
| PUT | `/students/<id>` | 200: updated student |
| DELETE | `/students/<id>` | 200: deletion confirmation |

POST and PUT require JSON strings named `name`, `department` and `email`.
Blank or invalid fields get 400, duplicate email gets 409, and missing IDs get 404.
Both add and update normalize email to lowercase. This classroom service has no
login because Task 1 does not require one; use fictional records.

## Test with cURL

The API must already be running. From a second terminal at the project root:

```text
python task1_students/curl_demo.py
```

This invokes the real cURL program, checks all five endpoints and confirms that a
deleted record returns 404. It creates a uniquely named sample record and removes it.

Manual Windows PowerShell examples:

```powershell
curl.exe http://127.0.0.1:5001/students
curl.exe -X POST http://127.0.0.1:5001/students -H "Content-Type: application/json" --data-binary "@task1_students/examples/student.json"
curl.exe http://127.0.0.1:5001/students/1
curl.exe -X PUT http://127.0.0.1:5001/students/1 -H "Content-Type: application/json" --data-binary "@task1_students/examples/student_updated.json"
curl.exe -X DELETE http://127.0.0.1:5001/students/1
```

Replace `1` with the `id` returned by POST. On macOS/Linux use `curl` instead of
`curl.exe`; the remaining arguments work the same way. The manual sample email
must be changed or its existing record removed before repeating the POST.

## Frontend behavior

The table is populated by GET requests. Add, update and delete each call the
corresponding Flask endpoint. A successful operation triggers `st.rerun()`, which
fetches fresh records. The update selector fetches the chosen student's details.
Deletion requires a checkbox so a single stray click does not remove a record.

See demo.mp4 and DEMONSTRATION.md for the walkthrough.
