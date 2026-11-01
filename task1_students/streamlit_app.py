"""Task 1 frontend. Every operation goes through the Flask HTTP API."""

import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.environ.get("STUDENTS_API_URL", "http://127.0.0.1:5001").rstrip("/")
st.set_page_config(page_title="Student Management", page_icon="🎓", layout="wide")


def api_request(method, path, payload=None):
    try:
        response = requests.request(method, API_URL + path, json=payload, timeout=5)
    except requests.RequestException:
        st.error("Cannot reach the Flask API. Start task1_students/app.py, then click Refresh records.")
        return None
    try:
        data = response.json()
    except ValueError:
        st.error("The API returned an unexpected response.")
        return None
    if not response.ok:
        st.error(data.get("error", "The request failed."))
        return None
    return data


def success(message):
    # Rerunning fetches fresh database records before drawing the table again.
    st.session_state["notice"] = message
    st.rerun()


st.title("Student Management")
st.caption("CSC3109 · Task 1 · Flask API + SQLite + Streamlit")
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))

if st.button("Refresh records"):
    st.rerun()

students = api_request("GET", "/students")
if students is None:
    st.stop()

st.subheader(f"Student records ({len(students)})")
if students:
    frame = pd.DataFrame(students)[["id", "name", "department", "email"]]
    st.dataframe(frame, hide_index=True, width="stretch")
else:
    st.info("No students yet. Add the first student below.")

action = st.radio("Choose an action", ["Add student", "Update student", "Delete student"], horizontal=True)

if action == "Add student":
    with st.form("add_student", clear_on_submit=True):
        name = st.text_input("Name", max_chars=100)
        department = st.text_input("Department", max_chars=100)
        email = st.text_input("Email", max_chars=254)
        submitted = st.form_submit_button("Add student", type="primary")
    if submitted:
        result = api_request("POST", "/students", {"name": name, "department": department, "email": email})
        if result is not None:
            success(f"Student #{result['id']} added. Records refreshed.")

elif not students:
    st.info("Add a student before updating or deleting records.")

else:
    by_id = {row["id"]: row for row in students}
    selected_id = st.selectbox(
        "Select a student", list(by_id),
        format_func=lambda sid: f"{sid} - {by_id[sid]['name']}",
    )
    # This also demonstrates the GET /students/<id> endpoint.
    selected = api_request("GET", f"/students/{selected_id}")
    if selected is None:
        st.stop()

    if action == "Update student":
        with st.form(f"update_{selected_id}"):
            name = st.text_input("Name", value=selected["name"], max_chars=100)
            department = st.text_input("Department", value=selected["department"], max_chars=100)
            email = st.text_input("Email", value=selected["email"], max_chars=254)
            submitted = st.form_submit_button("Save changes", type="primary")
        if submitted:
            result = api_request("PUT", f"/students/{selected_id}",
                                 {"name": name, "department": department, "email": email})
            if result is not None:
                success(f"Student #{selected_id} updated. Records refreshed.")

    else:
        st.warning(f"Delete {selected['name']}? This removes the database record.")
        confirmed = st.checkbox("I confirm this deletion", key=f"confirm_{selected_id}")
        if st.button("Delete selected student", type="primary", disabled=not confirmed):
            result = api_request("DELETE", f"/students/{selected_id}")
            if result is not None:
                success(f"Student #{selected_id} deleted. Records refreshed.")
