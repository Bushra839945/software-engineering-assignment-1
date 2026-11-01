"""Task 2: validate X-API-Key before processing any text."""

import hashlib
import json
import os
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        KEY_FILE=os.environ.get("API_KEY_FILE", str(Path(__file__).with_name("api_keys.json"))),
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if config:
        app.config.update(config)
    key_file = Path(app.config["KEY_FILE"])
    if not key_file.exists():
        raise RuntimeError("First run: python task2_api_keys/generate_keys.py")
    registry = json.loads(key_file.read_text(encoding="utf-8"))
    if not isinstance(registry, dict) or len(registry) != 3:
        raise RuntimeError("Expected three consumer key hashes in api_keys.json.")

    @app.errorhandler(HTTPException)
    def json_error(error):
        return jsonify(error=error.description), error.code

    @app.post("/process")
    def process_text():
        key = request.headers.get("X-API-Key", "")
        if not key:
            return jsonify(error="Missing X-API-Key header."), 401
        consumer = registry.get(hashlib.sha256(key.encode()).hexdigest())
        if consumer is None:
            return jsonify(error="Invalid API key."), 401
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get("text"), str):
            return jsonify(error='Send a JSON object containing a string named "text".'), 400
        if not data["text"].strip():
            return jsonify(error="text must not be blank."), 400
        if len(data["text"]) > 10000:
            return jsonify(error="text must be at most 10000 characters."), 400
        return jsonify(consumer=consumer, processed_text=data["text"].upper())

    return app


if __name__ == "__main__":
    create_app().run(host=os.environ.get("API_HOST", "127.0.0.1"), port=5002, debug=False)
