# Understand the assignment

## Six terms in simple English

| Term | Meaning in this project |
| --- | --- |
| API | A way for one program to ask another program to do something. |
| Endpoint | An API address together with an HTTP method, such as `GET /students`. |
| JSON | The format used to send fields such as `{"name": "Ayesha"}`. |
| Flask | The Python tool that receives requests and sends responses. |
| SQLite | A database stored in a local file. It remembers records after a restart. |
| Streamlit | The Python tool that builds Task 1's visible web interface. |

## Task 1: how a student reaches the database

When Add student is clicked, Streamlit sends the form fields to `POST /students`.
Flask checks the input, inserts a row into SQLite, and returns the new record with
status 201. Streamlit then reruns its screen, asks `GET /students` for fresh data,
and redraws the table. The frontend never directly opens the database.

`id` is the student ID. SQLite automatically assigns it. `name`, `department` and
`email` are editable. The same email cannot belong to two student records.

`GET` reads, `POST` creates, `PUT` updates, and `DELETE` removes. In this project,
PUT requires all three editable fields. Database queries use `?` placeholders,
so submitted values are treated as data rather than pieces of SQL code.

In `app.py`, `create_app()` builds the server and initializes the table.
`get_db()` supplies a database connection. `validate_student()` checks submitted
fields. Each decorated function handles one endpoint. In `streamlit_app.py`,
`api_request()` calls Flask, and `success()` triggers the automatic refresh.

## Task 2: how the key identifies a consumer

`generate_keys.py` uses `secrets.token_urlsafe(32)` to generate one unpredictable
key for each of three consumers. It saves the plaintext keys to private local
files, and saves their SHA-256 hashes in `api_keys.json`.

A consumer sends a key in the `X-API-Key` request header. Flask hashes that key
and looks for its hash in the registry. A matching key identifies a consumer.
The server then converts the submitted text to uppercase. A missing or incorrect
key gets 401 before any text is processed.

A hash is a one-way fingerprint. The server does not need the original plaintext
keys to check a supplied key. The private files are still needed for delivery to
the testers, so they must not be included in the public repository.

## Task 3: identity and permission are different

**Authentication asks: who are you?** The `/login` endpoint checks a username
and password. Passwords are stored as hashes, not plaintext. Successful login
sets a signed session cookie. cURL stores that cookie with `-c` and sends it back
with `-b` on later requests.

**Authorization asks: are you allowed to do this?** After recognizing the user,
the server reads the user's role from the database. An employee can only view.
An administrator can view, add, update and delete. Sending `"role":"administrator"`
in a login body does not change a user's actual role.

The `require_login()` decorator checks login before a protected function runs.
`require_login(admin_only=True)` also requires the administrator role.
The signed cookie contains a user ID, not a password. The secret used to sign
cookies is generated locally and kept in `.session_secret`.

Accounts and employee records are separate: the `users` table is for login and
roles, while `employees` contains the business records. Adding an employee record
does not create a new login account.

## HTTP statuses used

| Code | Meaning | Example |
| --- | --- | --- |
| 200 | Request succeeded | Reading or updating a record |
| 201 | Record created | Adding a student |
| 400 | Submitted data is invalid | Missing name or non-string text |
| 401 | Authentication is missing or invalid | No API key or incorrect password |
| 403 | Logged in but not permitted | Employee tries to delete a record |
| 404 | Record or endpoint not found | Reading a deleted student |
| 409 | Existing data conflicts | Duplicate email address |

## Practice explaining these points

1. Why does Task 1 need both Flask and Streamlit?
   Flask manages the API and database. Streamlit provides the visible forms and table.
2. Why is the data still present after restarting Flask?
   It is saved in a SQLite file, rather than only in a Python list in memory.
3. Where does a consumer put the API key?
   In the `X-API-Key` HTTP header.
4. Why can a valid employee login still receive 403?
   The identity is accepted, but that role lacks permission for the requested action.
5. Why should a public repository exclude keys and passwords?
   Anyone can read public repository files and reuse exposed credentials.
6. What does the browser refresh do after an update?
   It runs a fresh GET request and displays the database's current records.
