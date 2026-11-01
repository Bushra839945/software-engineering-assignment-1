"""Task 1: Flask is the only component that reads/writes the SQLite database."""

import os
import re
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException


def get_db():
    """Reuse one database connection per request; close it when the request ends."""
    if "db" not in g:
        from flask import current_app
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def validate_student(data):
    """PUT replaces all editable fields, so all three fields are required."""
    if not isinstance(data, dict):
        return None, "Send a JSON object with name, department and email."
    clean = {}
    for field, limit in (("name", 100), ("department", 100), ("email", 254)):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            return None, f"{field} must be a non-empty string."
        if len(value.strip()) > limit:
            return None, f"{field} must be at most {limit} characters."
        clean[field] = value.strip()
    clean["email"] = clean["email"].lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", clean["email"]):
        return None, "Enter an email such as student@example.com."
    return clean, None


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get("STUDENTS_DATABASE", str(Path(__file__).with_name("students.db"))),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if config:
        app.config.update(config)

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.errorhandler(HTTPException)
    def json_error(error):
        return jsonify(error=error.description), error.code

    with app.app_context():
        get_db().execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)
        get_db().commit()

    @app.get("/students")
    def list_students():
        rows = get_db().execute("SELECT * FROM students ORDER BY id").fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get("/students/<int:student_id>")
    def get_student(student_id):
        row = get_db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        if row is None:
            return jsonify(error="Student not found."), 404
        return jsonify(dict(row))

    @app.post("/students")
    def add_student():
        data, error = validate_student(request.get_json(silent=True))
        if error:
            return jsonify(error=error), 400
        db = get_db()
        try:
            cursor = db.execute(
                "INSERT INTO students (name, department, email) VALUES (?, ?, ?)",
                (data["name"], data["department"], data["email"]),
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return jsonify(error="This email already belongs to a student."), 409
        return jsonify(id=cursor.lastrowid, **data), 201

    @app.put("/students/<int:student_id>")
    def update_student(student_id):
        db = get_db()
        if db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone() is None:
            return jsonify(error="Student not found."), 404
        data, error = validate_student(request.get_json(silent=True))
        if error:
            return jsonify(error=error), 400
        try:
            db.execute(
                "UPDATE students SET name = ?, department = ?, email = ? WHERE id = ?",
                (data["name"], data["department"], data["email"], student_id),
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return jsonify(error="This email already belongs to a student."), 409
        return jsonify(id=student_id, **data)

    @app.delete("/students/<int:student_id>")
    def delete_student(student_id):
        db = get_db()
        cursor = db.execute("DELETE FROM students WHERE id = ?", (student_id,))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify(error="Student not found."), 404
        return jsonify(message="Student deleted.", id=student_id)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5001, debug=False)
