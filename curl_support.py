"""Shared demonstration utility: runs the real cURL executable, not requests."""

import json
import shutil
import subprocess
from pathlib import Path


class CurlDemo:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.entries = []
        self.curl = shutil.which("curl.exe") or shutil.which("curl")
        if not self.curl:
            raise SystemExit("cURL is missing. Install cURL, then run this demonstration again.")

    def request(self, title, method, path, expected, body=None, headers=None,
                cookie_file=None, safe_headers=None, safe_body=None):
        command = [self.curl, "--silent", "--show-error", "--max-time", "10",
                   "--write-out", "\nHTTP_STATUS:%{http_code}", "-X", method,
                   self.base_url + path]
        displayed = [f"curl -X {method} {self.base_url + path}"]
        for name, value in (headers or {}).items():
            command.extend(["-H", f"{name}: {value}"])
            visible = (safe_headers or {}).get(name, "[hidden]")
            displayed.append(f'  -H "{name}: {visible}"')
        if cookie_file:
            command.extend(["-b", str(cookie_file), "-c", str(cookie_file)])
            displayed.append(f"  -b {Path(cookie_file).name} -c {Path(cookie_file).name}")
        if body is not None:
            command.extend(["-H", "Content-Type: application/json", "--data-binary", "@-"])
            displayed.append('  -H "Content-Type: application/json" --data-binary @-')
            displayed.append("  JSON input: " + json.dumps(safe_body if safe_body is not None else body))
        result = subprocess.run(command, input=json.dumps(body) if body is not None else None,
                                capture_output=True, text=True)
        if result.returncode:
            # Do not print the raw command: it may contain a consumer's secret key.
            raise SystemExit(f"cURL failed (exit {result.returncode}). Check that the API is running at {self.base_url}.")
        raw, status = result.stdout.rsplit("\nHTTP_STATUS:", 1)
        status = int(status)
        try:
            payload = json.loads(raw)
            output = json.dumps(payload, indent=2)
        except ValueError:
            payload, output = raw, raw
        entry = {"title": title, "command": "\n".join(displayed), "output": output,
                 "status": status, "expected": expected, "passed": status == expected}
        self.entries.append(entry)
        print(f"\n{title}\n{entry['command']}\n{output}\nHTTP {status} (expected {expected})", flush=True)
        if status != expected:
            raise AssertionError(f"{title}: expected HTTP {expected}, received {status}")
        return payload

    def save_if_requested(self, filename):
        if filename:
            Path(filename).write_text(json.dumps(self.entries, indent=2) + "\n", encoding="utf-8")
        print(f"\nPASS: {len(self.entries)} real cURL requests matched their expected HTTP status.")
