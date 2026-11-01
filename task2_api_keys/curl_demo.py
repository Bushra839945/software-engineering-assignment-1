"""Exercise all three keys with cURL. Never print the secret key values."""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from curl_support import CurlDemo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Optional sanitized JSON record of this run")
    args = parser.parse_args()
    demo = CurlDemo("http://127.0.0.1:5002")
    private = Path(os.environ.get("API_KEY_DIRECTORY", str(Path(__file__).with_name("private_consumers"))))
    for number in range(1, 4):
        key = (private / f"consumer_{number}.key").read_text(encoding="utf-8").strip()
        demo.request(f"Consumer {number}: valid API key", "POST", "/process", 200,
                     body={"text": f"hello from consumer {number}"}, headers={"X-API-Key": key},
                     safe_headers={"X-API-Key": f"$CONSUMER_{number}_KEY"})
    demo.request("Invalid API key is rejected", "POST", "/process", 401,
                 body={"text": "hello"}, headers={"X-API-Key": "invalid-key"},
                 safe_headers={"X-API-Key": "invalid-key"})
    demo.request("Missing API key is rejected", "POST", "/process", 401, body={"text": "hello"})
    demo.save_if_requested(args.output)
