#!/usr/bin/env python3
"""Tiny OpenAI-compatible whisper endpoint. Only needs faster-whisper (already installed)."""

import json
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler

from linuxwhisper.transcription.engine import TranscriptionEngine
from linuxwhisper.config.loader import load_config

config = load_config()
engine = TranscriptionEngine(model_size=config["model"], device="cpu")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/audio/transcriptions":
            self.send_error(404)
            return

        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        boundary = content_type.split("boundary=")[-1].encode()
        parts = body.split(b"--" + boundary)
        audio_data = None
        language = None

        for part in parts:
            if b"name=\"file\"" in part:
                audio_data = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]
            elif b"name=\"language\"" in part:
                val = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]
                language = val.decode().strip()

        if not audio_data:
            self.send_error(400, "No audio file")
            return

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=True) as tmp:
            tmp.write(audio_data)
            tmp.flush()
            text = engine.transcribe(tmp.name, language=language)

        resp = json.dumps({"text": text}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(resp))
        self.end_headers()
        self.wfile.write(resp)

    def log_message(self, fmt, *args):
        print(f"[whisper] {args[0]}")


if __name__ == "__main__":
    print("Whisper server on http://127.0.0.1:8787 (using linuxwhisper engine)")
    HTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
