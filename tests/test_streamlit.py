"""Exercise the real Streamlit form against a live temporary Flask API."""

import threading
from pathlib import Path

import requests
from streamlit.testing.v1 import AppTest
from werkzeug.serving import make_server

from task1_students.app import create_app


def test_streamlit_crud_refresh_and_selection(tmp_path, monkeypatch):
    app = create_app({"DATABASE": str(tmp_path / "students.db")})
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"
    monkeypatch.setenv("STUDENTS_API_URL", url)
    try:
        ui = Path(__file__).resolve().parents[1] / "task1_students/streamlit_app.py"
        at = AppTest.from_file(str(ui), default_timeout=15).run()
        assert not at.exception
        for name, email in [("Ayesha Demo", "ayesha@example.com"), ("Bilal Demo", "bilal@example.com")]:
            at.text_input[0].input(name)
            at.text_input[1].input("Computer Science")
            at.text_input[2].input(email)
            at.button[1].click().run()
            assert not at.exception
            assert "added" in at.success[0].value
        assert len(at.dataframe[0].value) == 2
        at.radio[0].set_value("Update student").run()
        at.selectbox[0].set_value(2).run()
        assert at.text_input[0].value == "Bilal Demo"
        at.text_input[1].input("Software Engineering")
        at.button[1].click().run()
        assert not at.exception
        assert "updated" in at.success[0].value
        assert requests.get(url + "/students/2", timeout=5).json()["department"] == "Software Engineering"
        assert at.dataframe[0].value.loc[1, "department"] == "Software Engineering"
        at.selectbox[0].set_value(1).run()
        assert at.text_input[0].value == "Ayesha Demo"
        at.radio[0].set_value("Delete student").run()
        assert at.button[1].disabled
        at.checkbox[0].check().run()
        at.button[1].click().run()
        assert not at.exception
        assert "deleted" in at.success[0].value
        assert len(at.dataframe[0].value) == 1
        assert requests.get(url + "/students/1", timeout=5).status_code == 404
    finally:
        server.shutdown()
        thread.join(timeout=5)
