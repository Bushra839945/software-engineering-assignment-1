# Task 3: Authentication and authorization

## Run

Use the root launcher and choose **3**. It prompts you to create passwords on
the first run. Usernames are `employee` and `admin`; choose your own passwords.
Typing is hidden, including the cursor movement. Existing accounts are retained.

For separate commands, from the project root with the environment's Python:

```text
python task3_auth/setup_users.py
python task3_auth/app.py
```

The API runs at `http://127.0.0.1:5003`. Login accounts and records are stored in
`employees.db`. Passwords are hashed by Werkzeug. A random `.session_secret`
signs cookies. Both files are local and excluded from the public repository.

## Role permissions

| Endpoint | No valid login | Employee | Administrator |
| --- | --- | --- | --- |
| GET `/employees` | 401 | 200 | 200 |
| GET `/employees/<id>` | 401 | Allowed | Allowed |
| POST `/employees` | 401 | 403 | Allowed |
| PUT `/employees/<id>` | 401 | 403 | Allowed |
| DELETE `/employees/<id>` | 401 | 403 | Allowed |

Allowed requests still need valid data and existing IDs where appropriate.
POST/PUT require name, department and email. A duplicate email returns 409.

`POST /login` takes a JSON username and password. A valid login sets a signed
HTTP-only session cookie and returns the database role. Incorrect credentials
get 401. `POST /logout` clears the client's session. Sessions expire after
30 minutes of inactivity. Roles are read from the users table on each request.

## Full cURL demonstration

Keep the server running. In a second terminal run:

```text
python task3_auth/curl_demo.py
```

Enter the two passwords when prompted. The script executes actual cURL commands
and checks 15 results: no login, invalid credentials, employee login/read/write
restrictions, admin login/view/add/update/delete, and access after logout. It
creates a sample employee and deletes it. Temporary cookies are removed at the end.
Passwords and cookie contents are not printed.

## Manual cURL testing on Windows

Login through the supplied helper, which prompts privately and invokes cURL:

```powershell
.\.venv\Scripts\python.exe task3_auth/login_with_curl.py employee
curl.exe -b task3_auth/employee.cookies http://127.0.0.1:5003/employees
curl.exe -X POST -b task3_auth/employee.cookies http://127.0.0.1:5003/employees -H "Content-Type: application/json" --data-binary "@task3_auth/examples/employee.json"
```

Reading succeeds. Adding returns 403 because the employee role is not permitted.
To include the status in any manual response, add `-w "\nHTTP %{http_code}\n"`.

Now use the administrator's cookie:

```powershell
.\.venv\Scripts\python.exe task3_auth/login_with_curl.py admin
curl.exe -X POST -b task3_auth/admin.cookies http://127.0.0.1:5003/employees -H "Content-Type: application/json" --data-binary "@task3_auth/examples/employee.json"
curl.exe -X PUT -b task3_auth/admin.cookies http://127.0.0.1:5003/employees/1 -H "Content-Type: application/json" --data-binary "@task3_auth/examples/employee_updated.json"
curl.exe -X DELETE -b task3_auth/admin.cookies http://127.0.0.1:5003/employees/1
curl.exe -X POST -b task3_auth/admin.cookies -c task3_auth/admin.cookies http://127.0.0.1:5003/logout
curl.exe -b task3_auth/admin.cookies http://127.0.0.1:5003/employees
```

Replace `1` with the ID returned by POST. The final request gets 401 after logout.
On macOS/Linux use `.venv/bin/python` for Python and `curl` instead of `curl.exe`.
To test invalid credentials manually, run the login helper and enter a wrong
password; it displays the actual 401 response. Without `-b`, a protected endpoint
also returns 401.

**Authentication:** credentials must establish identity. **Authorization:** the
authenticated user's role must permit the operation. These are separate checks.

If a classroom password is forgotten, stop the server and remove your local
employees.db before rerunning setup_users.py. This resets all Task 3 accounts AND
records, so only do it when you are ready to discard that local demo data.
