"""Behavior checks use temporary databases and newly generated test credentials."""

import hashlib
import json
import secrets

import pytest
from werkzeug.security import generate_password_hash

from task1_students.app import create_app as students_app
from task2_api_keys.app import create_app as keys_app
from task2_api_keys.generate_keys import generate_keys
from task3_auth.app import create_app as auth_app, get_db


@pytest.fixture
def students(tmp_path):
    app = students_app({"TESTING": True, "DATABASE": str(tmp_path / "students.db")})
    return app.test_client()


STUDENT = {"name": "Ayesha Demo", "department": "Computer Science", "email": "ayesha@example.com"}


def test_student_full_crud_and_persistence(students):
    assert students.get("/students").json == []
    created = students.post("/students", json=STUDENT)
    assert created.status_code == 201
    sid = created.json["id"]
    assert students.get(f"/students/{sid}").json["name"] == "Ayesha Demo"
    changed = {**STUDENT, "department": "Software Engineering"}
    assert students.put(f"/students/{sid}", json=changed).status_code == 200
    reopened = students_app(dict(students.application.config)).test_client()
    assert reopened.get("/students").json[0]["department"] == "Software Engineering"
    assert students.delete(f"/students/{sid}").status_code == 200
    assert students.get("/students").json == []


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_student_missing_record(students, method):
    assert getattr(students, method)("/students/999").status_code == 404


@pytest.mark.parametrize("payload", [None, [], {}, {**STUDENT, "name": " "},
                                      {**STUDENT, "email": "bad"}, {**STUDENT, "name": 123}])
def test_student_invalid_input(students, payload):
    assert students.post("/students", json=payload).status_code == 400


def test_student_duplicate_email_case_insensitive(students):
    students.post("/students", json=STUDENT)
    assert students.post("/students", json={**STUDENT, "email": "AYESHA@example.com"}).status_code == 409
    second = students.post("/students", json={**STUDENT, "email": "other@example.com"}).json
    assert students.put(f"/students/{second['id']}", json=STUDENT).status_code == 409


def test_sql_like_text_is_stored_as_text(students):
    payload = {**STUDENT, "name": "Robert'); DROP TABLE students;--"}
    assert students.post("/students", json=payload).status_code == 201
    assert students.get("/students").json[0]["name"] == payload["name"]


@pytest.fixture
def keyed_api(tmp_path):
    private = generate_keys(tmp_path)
    keys = [p.read_text().strip() for p in sorted(private.glob("*.key"))]
    registry = json.loads((tmp_path / "api_keys.json").read_text())
    assert len(set(keys)) == 3
    assert all(key not in registry for key in keys)
    assert all(hashlib.sha256(key.encode()).hexdigest() in registry for key in keys)
    app = keys_app({"TESTING": True, "KEY_FILE": str(tmp_path / "api_keys.json")})
    return app.test_client(), keys


@pytest.mark.parametrize("index", [0, 1, 2])
def test_each_consumer_key(keyed_api, index):
    client, keys = keyed_api
    response = client.post("/process", headers={"X-API-Key": keys[index]}, json={"text": "hello university"})
    assert response.status_code == 200
    assert response.json == {"consumer": f"consumer_{index+1}", "processed_text": "HELLO UNIVERSITY"}


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "not-a-valid-key"}])
def test_reject_missing_and_invalid_keys_before_processing(keyed_api, headers):
    client, _ = keyed_api
    assert client.post("/process", headers=headers, json={"text": "hello"}).status_code == 401


@pytest.mark.parametrize("payload", [{}, {"text": 12}, {"text": " "}, [], {"text": "x" * 10001}])
def test_text_validation(keyed_api, payload):
    client, keys = keyed_api
    assert client.post("/process", headers={"X-API-Key": keys[0]}, json=payload).status_code == 400


def test_key_generator_does_not_overwrite(tmp_path):
    generate_keys(tmp_path)
    with pytest.raises(FileExistsError):
        generate_keys(tmp_path)


@pytest.fixture
def auth(tmp_path):
    app = auth_app({"TESTING": True, "DATABASE": str(tmp_path / "employees.db"),
                    "SECRET_KEY": secrets.token_hex(32)})
    passwords = {"employee": secrets.token_urlsafe(16), "admin": secrets.token_urlsafe(16)}
    with app.app_context():
        for username, role in (("employee", "employee"), ("admin", "administrator")):
            get_db().execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                             (username, generate_password_hash(passwords[username]), role))
        get_db().execute("INSERT INTO employees (name, department, email) VALUES (?, ?, ?)",
                         ("Demo Person", "IT", "demo@example.com"))
        get_db().commit()
    return app.test_client(), passwords


@pytest.mark.parametrize("method,path", [("get", "/employees"), ("get", "/employees/1"),
                                         ("post", "/employees"), ("put", "/employees/1"),
                                         ("delete", "/employees/1")])
def test_all_employee_endpoints_require_login(auth, method, path):
    client, _ = auth
    assert getattr(client, method)(path, json=STUDENT).status_code == 401


def test_bad_login_and_role_escalation(auth):
    client, passwords = auth
    assert client.post("/login", json={"username": "employee", "password": "wrong"}).status_code == 401
    assert client.post("/login", json={"username": "missing", "password": "wrong"}).status_code == 401
    response = client.post("/login", json={"username": "employee", "password": passwords["employee"], "role": "administrator"})
    assert response.json["role"] == "employee"
    assert client.get("/employees").status_code == 200
    assert client.get("/employees/1").status_code == 200
    assert client.post("/employees", json=STUDENT).status_code == 403


@pytest.mark.parametrize("method,path", [("post", "/employees"), ("put", "/employees/1"), ("delete", "/employees/1")])
def test_employee_cannot_write(auth, method, path):
    client, passwords = auth
    client.post("/login", json={"username": "employee", "password": passwords["employee"]})
    assert getattr(client, method)(path, json=STUDENT).status_code == 403
    assert client.get("/employees/1").json["name"] == "Demo Person"


def test_admin_full_crud_and_logout(auth):
    client, passwords = auth
    assert client.post("/login", json={"username": "admin", "password": passwords["admin"]}).status_code == 200
    created = client.post("/employees", json=STUDENT)
    assert created.status_code == 201
    eid = created.json["id"]
    assert client.get("/employees").status_code == 200
    assert client.get(f"/employees/{eid}").status_code == 200
    assert client.put(f"/employees/{eid}", json={**STUDENT, "department": "HR"}).status_code == 200
    assert client.get(f"/employees/{eid}").json["department"] == "HR"
    assert client.delete(f"/employees/{eid}").status_code == 200
    assert client.get(f"/employees/{eid}").status_code == 404
    assert client.post("/logout").status_code == 200
    assert client.get("/employees").status_code == 401


def test_invalid_session_cannot_authenticate(auth):
    client, _ = auth
    client.set_cookie("employee_session", "forged-cookie")
    assert client.get("/employees").status_code == 401


def test_admin_validation_and_duplicate(auth):
    client, passwords = auth
    client.post("/login", json={"username": "admin", "password": passwords["admin"]})
    assert client.post("/employees", json={}).status_code == 400
    assert client.post("/employees", json={**STUDENT, "email": "DEMO@example.com"}).status_code == 409
    assert client.put("/employees/999", json=STUDENT).status_code == 404
    assert client.delete("/employees/999").status_code == 404


@pytest.mark.parametrize("payload", [None, [], {}, {"username": "employee", "password": 12}])
def test_invalid_login_body(auth, payload):
    client, _ = auth
    assert client.post("/login", json=payload).status_code == 400
