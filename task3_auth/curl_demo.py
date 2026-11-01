"""Demonstrate authentication versus authorization with actual cURL requests."""

import argparse
import getpass
import os
import sys
import tempfile
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from curl_support import CurlDemo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Optional sanitized JSON record of this run")
    args = parser.parse_args()
    employee_password = os.environ.get("DEMO_EMPLOYEE_PASSWORD") or getpass.getpass("Employee password: ")
    admin_password = os.environ.get("DEMO_ADMIN_PASSWORD") or getpass.getpass("Administrator password: ")
    demo = CurlDemo("http://127.0.0.1:5003")
    person = {"name": "Bilal Demo", "department": "IT", "email": f"demo-{uuid.uuid4().hex[:8]}@example.com"}
    with tempfile.TemporaryDirectory() as folder:
        employee_cookie = Path(folder) / "employee.cookies"
        admin_cookie = Path(folder) / "admin.cookies"
        demo.request("No login: authentication required", "GET", "/employees", 401)
        demo.request("Wrong password: authentication fails", "POST", "/login", 401,
                     body={"username": "employee", "password": "wrong-password"},
                     safe_body={"username": "employee", "password": "[incorrect password]"})
        demo.request("Employee login: authentication succeeds", "POST", "/login", 200,
                     body={"username": "employee", "password": employee_password}, cookie_file=employee_cookie,
                     safe_body={"username": "employee", "password": "[hidden]"})
        demo.request("Employee can view records", "GET", "/employees", 200, cookie_file=employee_cookie)
        demo.request("Employee cannot add: authorization fails", "POST", "/employees", 403,
                     body=person, cookie_file=employee_cookie)
        demo.request("Administrator login", "POST", "/login", 200,
                     body={"username": "admin", "password": admin_password}, cookie_file=admin_cookie,
                     safe_body={"username": "admin", "password": "[hidden]"})
        created = demo.request("Administrator can add", "POST", "/employees", 201,
                               body=person, cookie_file=admin_cookie)
        path = f"/employees/{created['id']}"
        demo.request("Employee can view the new record", "GET", path, 200, cookie_file=employee_cookie)
        demo.request("Employee cannot update", "PUT", path, 403, body=person, cookie_file=employee_cookie)
        demo.request("Employee cannot delete", "DELETE", path, 403, cookie_file=employee_cookie)
        demo.request("Administrator can view all records", "GET", "/employees", 200, cookie_file=admin_cookie)
        demo.request("Administrator can update", "PUT", path, 200,
                     body={**person, "department": "Human Resources"}, cookie_file=admin_cookie)
        demo.request("Administrator can delete", "DELETE", path, 200, cookie_file=admin_cookie)
        demo.request("Administrator logs out", "POST", "/logout", 200, cookie_file=admin_cookie)
        demo.request("After logout: access denied", "GET", "/employees", 401, cookie_file=admin_cookie)
    demo.save_if_requested(args.output)
