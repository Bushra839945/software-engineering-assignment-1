# Instructions for the three assigned testers

The project owner privately gives one different key to each tester. The public
repository never supplies the actual keys. The owner should map consumer_1,
consumer_2 and consumer_3 to the assigned people privately.

## Choose how to reach the API

**Same computer:** the testers can take turns at the owner's running API using
their own keys. Use `http://127.0.0.1:5002/process`.

**Different computers on a trusted classroom/private network:** stop Task 2,
then start the API with `API_HOST` set to `0.0.0.0`. In PowerShell, from the project root:

```powershell
$env:API_HOST = "0.0.0.0"
.\.venv\Scripts\python.exe task2_api_keys/app.py
```

On macOS/Linux:

```bash
API_HOST=0.0.0.0 .venv/bin/python task2_api_keys/app.py
```

The testers replace `127.0.0.1` in their requests with the owner's private LAN
IPv4 address, such as `192.168.1.20`. Use `ipconfig` on Windows to find the active
network adapter's IPv4 address. `0.0.0.0` is a listening setting, not a URL to visit.
If needed, permit the program on the private network in the owner's firewall.
Some classroom/guest networks isolate devices, so same-computer testing is simpler.

This HTTP development server is for a trusted local exercise. For remote testers
over the internet, arrange an HTTPS deployment with your instructor; do not send
keys to a public HTTP address. A public code repository does not host the running API.

## Make your request without showing the key

Save your privately received key as `consumer_1.key` (or your assigned number).
Copy the non-secret `examples/text.json` file into the same folder. Open a terminal
in that folder. These commands assume tester 1; testers 2 and 3 use their own file.

PowerShell:

```powershell
$key = (Get-Content .\consumer_1.key -Raw).Trim()
$url = "http://127.0.0.1:5002/process"
curl.exe -w "\nHTTP %{http_code}\n" -X POST $url -H "X-API-Key: $key" -H "Content-Type: application/json" --data-binary "@text.json"
Remove-Variable key
```

macOS/Linux:

```bash
key="$(cat consumer_1.key)"
url="http://127.0.0.1:5002/process"
curl -w '\nHTTP %{http_code}\n' -X POST "$url" -H "X-API-Key: $key" -H "Content-Type: application/json" --data-binary @text.json
unset key
```

Change `$url`/`url` if testing from a different computer. Expect HTTP 200, your
consumer label, and uppercase text. The key itself must not appear in the output.

For the invalid-key check, repeat with `-H "X-API-Key: invalid-key"`. Expect 401.
For the missing-key check, omit the X-API-Key header. Expect 401.

Send the owner a screenshot or recording of the command using the variable and
the resulting JSON/status. Do not show the contents of the .key file or print the
key variable. Share the real key only privately, and remove it from the testing
computer when the exercise is finished.
