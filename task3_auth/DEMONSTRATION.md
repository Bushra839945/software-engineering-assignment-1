# Task 3 demonstration

Open **[demo.mp4](demo.mp4)**. This silent sample video renders actual cURL
commands/results as readable slides. Passwords are hidden and session cookies
are referred to by filenames; their contents are never displayed.

The 15 requests show unauthenticated access (401), wrong credentials (401),
employee login and reading (200), employee create/update/delete rejection (403),
administrator login and full CRUD, logout, and access denied after logout (401).

The employee and administrator accounts are distinct from the employee record
created during the demonstration. The sample record is removed at the end.

To reproduce: start Task 3, then run `python task3_auth/curl_demo.py` from the root
using the virtual environment's Python. Enter your two local passwords at the
hidden prompts. Temporary session cookies are deleted when the demonstration ends.

The key point to explain: authentication verifies identity; authorization checks
whether that identity's role permits the action. The same valid employee session
can therefore receive 200 for reading and 403 for writing.

This local verification was captured on 1 November 2026. It is a presentation of
actual execution results, not a personal screen recording by the submitting
student. Add your own narrated recording if requested by the instructor.
