"""Create local login accounts without putting passwords in the source code."""

import getpass

from app import create_app, get_db
from werkzeug.security import generate_password_hash


def ask_password(username):
    while True:
        password = getpass.getpass(f"Choose a password for {username} (8+ characters): ")
        confirm = getpass.getpass("Type it again: ")
        if len(password) < 8:
            print("Please use at least 8 characters.")
        elif password != confirm:
            print("Passwords did not match. Try again.")
        else:
            return password


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db = get_db()
        for username, role in (("employee", "employee"), ("admin", "administrator")):
            if db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
                print(f"{username} already exists; kept its password unchanged.")
                continue
            password = ask_password(username)
            db.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       (username, generate_password_hash(password), role))
            db.commit()
            print(f"Created {username} with the {role} role.")
        print("Accounts are ready. Next: python task3_auth/app.py (from the project root).")
