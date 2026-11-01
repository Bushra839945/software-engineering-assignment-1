# Task 2 demonstration

Open **[demo.mp4](demo.mp4)**. This silent sample video renders commands and
responses captured from actual local cURL execution. It is a presentation of
recorded results, not footage of someone typing in a terminal.

The five checks show:

1. Consumer 1's valid key returns 200 and uppercase text.
2. Consumer 2's different valid key returns 200.
3. Consumer 3's different valid key returns 200.
4. An invalid key returns 401.
5. A missing key returns 401.

Secret values are represented by variable names on screen. The keys used for
this verification are not in the package. Run the key generator to create your
own keys before testing your copy.

To reproduce: keep Task 2 running and execute `python task2_api_keys/curl_demo.py`
from the root with the virtual environment's Python. All five requests use the
real cURL executable. No secret is printed.

This verification was performed locally on 1 November 2026. It is **not evidence
that three assigned people tested the API**. Privately share one key with each
tester, let each run cURL, and add their sanitized evidence to TESTER_RESULTS.md.
Record your own explanation if your instructor requires it.
