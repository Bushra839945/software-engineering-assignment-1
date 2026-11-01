"""Run with the Task 1 API already running. Creates and deletes one demo row."""

import argparse
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from curl_support import CurlDemo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Optional sanitized JSON record of this run")
    args = parser.parse_args()
    demo = CurlDemo("http://127.0.0.1:5001")
    student = {"name": "Ayesha Demo", "department": "Computer Science",
               "email": f"demo-{uuid.uuid4().hex[:8]}@example.com"}
    demo.request("List students", "GET", "/students", 200)
    row = demo.request("Add a student", "POST", "/students", 201, body=student)
    path = f"/students/{row['id']}"
    demo.request("View one student", "GET", path, 200)
    demo.request("Update department", "PUT", path, 200, body={**student, "department": "Software Engineering"})
    demo.request("Delete the demo student", "DELETE", path, 200)
    demo.request("Deleted student is no longer found", "GET", path, 404)
    demo.save_if_requested(args.output)
