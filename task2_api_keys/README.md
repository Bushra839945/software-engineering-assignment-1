# Task 2: Three API consumers

## Run

Use the root launcher and choose **2**. The first run generates the keys.
For separate commands, run from the project root with the environment's Python:

```text
python task2_api_keys/generate_keys.py
python task2_api_keys/app.py
```

The generator refuses to overwrite existing keys. Each consumer's key is saved
privately as `private_consumers/consumer_1.key`, `consumer_2.key`, or
`consumer_3.key`. The API stores only their SHA-256 hashes in `api_keys.json`.
None of those generated files belongs in the public repository.

## API contract

`POST http://127.0.0.1:5002/process`

- Header: `X-API-Key: <the consumer's actual private key>`
- Header: `Content-Type: application/json`
- Body: `{"text":"hello"}`
- Valid key: 200 with `{"consumer":"consumer_1","processed_text":"HELLO"}`.
- Missing or invalid key: 401, with no processing result.
- Valid key but invalid/blank text: 400.

## Demonstrate with real cURL

Leave the API running and use a second terminal:

```text
python task2_api_keys/curl_demo.py
```

The script runs cURL five times: once with each valid key, once with an invalid
key and once with no key. It shows consumer names and results while hiding the
actual secret values. This local script is an implementation demonstration;
three actual assigned consumers still need to test separately.

Manual Windows PowerShell request from the project root:

```powershell
$key = (Get-Content task2_api_keys/private_consumers/consumer_1.key -Raw).Trim()
curl.exe -X POST http://127.0.0.1:5002/process -H "X-API-Key: $key" -H "Content-Type: application/json" --data-binary "@task2_api_keys/examples/text.json"
Remove-Variable key
```

macOS/Linux:

```bash
key="$(cat task2_api_keys/private_consumers/consumer_1.key)"
curl -X POST http://127.0.0.1:5002/process -H "X-API-Key: $key" -H "Content-Type: application/json" --data-binary @task2_api_keys/examples/text.json
unset key
```

Repeat with consumer_2.key and consumer_3.key. To check rejection, use
`-H "X-API-Key: invalid-key"`; to check a missing key, omit that header.
Never use `curl -v` or shell tracing in a public recording, because they can
display the actual request header.

## Sharing and tester evidence

See TESTER_INSTRUCTIONS.md. Give each assigned consumer ONLY their own key using
a private channel. Do not publish the files or put keys in public video frames.
Record the testers' sanitized results in TESTER_RESULTS.md after they run cURL.
For deliberate rotation later, stop the API, delete your old private key files and
registry locally, generate a new set, restart and privately redistribute the keys.
