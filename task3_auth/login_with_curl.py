"""Prompt privately and use cURL to save a local session cookie for manual tests."""

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from curl_support import CurlDemo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username", choices=["employee", "admin"])
    args = parser.parse_args()
    cookie = Path(__file__).with_name(f"{args.username}.cookies")
    password = getpass.getpass(f"Password for {args.username}: ")
    demo = CurlDemo("http://127.0.0.1:5003")
    try:
        demo.request("Log in and save the session", "POST", "/login", 200,
                     body={"username": args.username, "password": password}, cookie_file=cookie,
                     safe_body={"username": args.username, "password": "[hidden]"})
    except AssertionError:
        raise SystemExit("Login was rejected. Check the username and password.")
    cookie.chmod(0o600)
    print(f"Session saved privately to {cookie.name}. Do not publish or film its contents.")
