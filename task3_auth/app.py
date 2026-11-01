"""Task 3: login proves identity; role checks decide which actions are allowed."""

import os
import re
import secrets
import sqlite3
from datetime import timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, current_app, g, jsonify, request, session
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def require_login(admin_only=False):
    """A decorator runs these permission checks before the protected endpoint."""
    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user_id = session.get("user_id")
            user = get_db().execute(
                "SELECT id, username, role FROM users WHERE id = ?", (user_id,)
            ).fetchone() if user_id is not None else None
            if user is None:
                return jsonify(error="Login required."), 401
            if admin_only and user["role"] != "administrator":
                return jsonify(error="Administrator permission required."), 403
            g.user = user
            return view(*args, **kwargs)
        return wrapped
    return decorate


def validate_employee(data):
    if not isinstance(data, dict):
        return None, "Send a JSON object with name, department and email."
    clean = {}
    for field, limit in (("name", 100), ("department", 100), ("email", 254)):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
            return None, f"{field} must be a non-empty string of at most {limit} characters."
        clean[field] = value.strip()
    clean["email"] = clean["email"].lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", clean["email"]):
        return None, "Enter a valid email address."
    return clean, None


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get("EMPLOYEES_DATABASE", str(Path(__file__).with_name("employees.db"))),
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY"),
        SECRET_FILE=str(Path(__file__).with_name(".session_secret")),
        SESSION_COOKIE_NAME="employee_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if config:
        app.config.update(config)
    if not app.config["SECRET_KEY"]:
        secret_file = Path(app.config["SECRET_FILE"])
        if not secret_file.exists():
            # Exclusive creation avoids silently replacing another process's secret.
            try:
                with secret_file.open("x", encoding="utf-8") as handle:
                    handle.write(secrets.token_hex(32))
                secret_file.chmod(0o600)
            except FileExistsError:
                pass
        app.config["SECRET_KEY"] = secret_file.read_text(encoding="utf-8").strip()
    if len(app.config["SECRET_KEY"]) < 32:
        raise RuntimeError("The session secret must have at least 32 characters.")

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.errorhandler(HTTPException)
    def json_error(error):
        return jsonify(error=error.description), error.code

    with app.app_context():
        get_db().executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('employee', 'administrator'))
            );
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );
        """)
        get_db().commit()

    @app.post("/login")
    def login():
        session.clear()
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Send username and password in a JSON object."), 400
        username, password = data.get("username"), data.get("password")
        if not isinstance(username, str) or not isinstance(password, str) or not username or not password:
            return jsonify(error="username and password are required strings."), 400
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            return jsonify(error="Invalid username or password."), 401
        session["user_id"] = user["id"]
        session.permanent = True
        return jsonify(message="Login successful.", username=user["username"], role=user["role"])

    @app.post("/logout")
    @require_login()
    def logout():
        session.clear()
        return jsonify(message="Logged out.")

    @app.get("/employees")
    @require_login()
    def list_employees():
        return jsonify([dict(row) for row in get_db().execute("SELECT * FROM employees ORDER BY id")])

    @app.get("/employees/<int:employee_id>")
    @require_login()
    def get_employee(employee_id):
        row = get_db().execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
        if row is None:
            return jsonify(error="Employee not found."), 404
        return jsonify(dict(row))

    @app.post("/employees")
    @require_login(admin_only=True)
    def add_employee():
        data, error = validate_employee(request.get_json(silent=True))
        if error:
            return jsonify(error=error), 400
        db = get_db()
        try:
            cursor = db.execute(
                "INSERT INTO employees (name, department, email) VALUES (?, ?, ?)",
                (data["name"], data["department"], data["email"]),
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return jsonify(error="This email already belongs to an employee."), 409
        return jsonify(id=cursor.lastrowid, **data), 201

    @app.put("/employees/<int:employee_id>")
    @require_login(admin_only=True)
    def update_employee(employee_id):
        db = get_db()
        if db.execute("SELECT id FROM employees WHERE id = ?", (employee_id,)).fetchone() is None:
            return jsonify(error="Employee not found."), 404
        data, error = validate_employee(request.get_json(silent=True))
        if error:
            return jsonify(error=error), 400
        try:
            db.execute("UPDATE employees SET name = ?, department = ?, email = ? WHERE id = ?",
                       (data["name"], data["department"], data["email"], employee_id))
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return jsonify(error="This email already belongs to an employee."), 409
        return jsonify(id=employee_id, **data)

    @app.delete("/employees/<int:employee_id>")
    @require_login(admin_only=True)
    def delete_employee(employee_id):
        db = get_db()
        cursor = db.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify(error="Employee not found."), 404
        return jsonify(message="Employee deleted.", id=employee_id)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5003, debug=False)
