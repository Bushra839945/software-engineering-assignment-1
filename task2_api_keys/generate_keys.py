"""Create exactly three API keys. Plaintext keys stay in private local files."""

import hashlib
import json
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def generate_keys(directory=ROOT):
    directory = Path(directory)
    registry = directory / "api_keys.json"
    private_dir = directory / "private_consumers"
    if registry.exists() or private_dir.exists():
        raise FileExistsError("Keys already exist. Keep them; do not overwrite active testers' keys.")
    directory.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(mode=0o700)
    hashes = {}
    for number in range(1, 4):
        consumer = f"consumer_{number}"
        key = secrets.token_urlsafe(32)
        hashes[hashlib.sha256(key.encode()).hexdigest()] = consumer
        key_file = private_dir / f"{consumer}.key"
        key_file.write_text(key + "\n", encoding="utf-8")
        key_file.chmod(0o600)
    registry.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    registry.chmod(0o600)
    return private_dir


if __name__ == "__main__":
    try:
        folder = generate_keys()
        print("Created three unique consumer keys.")
        print(f"Private files: {folder}")
        print("Share each .key file privately with its assigned tester. Do not upload or film its contents.")
    except FileExistsError as error:
        raise SystemExit(str(error))
