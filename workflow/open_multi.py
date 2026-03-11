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

    for item in urls:
        if isinstance(item, str):
            subprocess.run(["open", item], check=False)
            continue

        if not isinstance(item, dict):
            continue

        url = item.get("url", "").strip()
        if not url:
            continue

        browser_app = item.get("browser_app", "").strip()
        if browser_app:
            subprocess.run(["open", "-a", browser_app, url], check=False)
            continue

        subprocess.run(["open", url], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
