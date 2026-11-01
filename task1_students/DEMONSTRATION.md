# Task 1 demonstration

Open **[demo.mp4](demo.mp4)**. This sample video has no audio; on-screen commands,
responses and the browser interface provide the explanation.

The first part presents sanitized results from six actual cURL requests against
the local Flask API: list, add, retrieve one, update, delete, and retrieve the
deleted record (404). The results are rendered as readable slides; they are not
a recording of someone typing at a terminal.

The second part is an actual automated browser recording of the Streamlit app.
It adds a fictional student, updates the department, confirms deletion and shows
the refreshed records after every change. The API is running against SQLite.

To reproduce the API portion, run the server and execute
`python task1_students/curl_demo.py` from the project root with the virtual
environment's Python. To record your own interface demonstration, start Task 1
and follow the actions above while explaining the Flask/API/database flow.

The sample was captured during local verification on 1 November 2026. It does
not claim to be a personal recording by the submitting student.
