#!/usr/bin/env python3
import base64
import json
import subprocess
import sys


def decode_payload(payload: str):
    padded = payload + "=" * (-len(payload) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    return json.loads(raw.decode("utf-8"))


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        return 1

    try:
        urls = decode_payload(sys.argv[1].strip())
    except Exception:
        return 2

    for url in urls:
        subprocess.run(["open", url], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
