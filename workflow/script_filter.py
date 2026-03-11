#!/usr/bin/env python3
import base64
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
PROMPT_TEMPLATES = json.loads((CONFIG_DIR / "templates.json").read_text(encoding="utf-8"))
PLATFORMS = json.loads((CONFIG_DIR / "platforms.json").read_text(encoding="utf-8"))


def get_clipboard() -> str:
    try:
        return subprocess.check_output(["pbpaste"], universal_newlines=True).strip()
    except Exception:
        return ""


def env_enabled(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_value(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def clean_preview(text: str, limit: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1] + "…"


def json_print(items):
    print(json.dumps({"items": items}, ensure_ascii=False))


def platform_url_template(platform_key: str) -> str:
    platform = PLATFORMS[platform_key]
    env_name = f"url_{platform_key}"
    return env_value(env_name, platform["url"])


def platform_browser_app(platform_key: str) -> str:
    platform = PLATFORMS[platform_key]
    env_name = f"browser_{platform_key}"
    return env_value(env_name, platform.get("browser_app", ""))


def build_url(platform_key: str, final_prompt: str, autosend: str) -> str:
    encoded_prompt = urllib.parse.quote(final_prompt)
    template = platform_url_template(platform_key)
    if "%s" in template:
        return template.replace("%s", encoded_prompt)
    separator = "&" if "?" in template else "?"
    if template.endswith("=") or template.endswith("/"):
        base = template
    else:
        base = f"{template}{separator}prompt="
    return f"{base}{encoded_prompt}&autosend={autosend}"


def build_open_target(platform_key: str, final_prompt: str, autosend: str):
    target = {"url": build_url(platform_key, final_prompt, autosend)}
    browser_app = platform_browser_app(platform_key)
    if browser_app:
        target["browser_app"] = browser_app
    return target


def build_platform_items(final_prompt: str, mode_subtitle: str):
    autosend = os.getenv("autosend", "1")
    items = []

    enabled_multi_keys = [
        key for key, platform in PLATFORMS.items()
        if env_enabled(f"enable_{key}", default=platform.get("enabled_by_default", True))
    ]

    for key, platform in PLATFORMS.items():
        open_target = build_open_target(key, final_prompt, autosend)
        single_payload = base64.urlsafe_b64encode(
            json.dumps([open_target], ensure_ascii=False).encode("utf-8")
        ).decode("ascii")
        enabled_text = "[x]" if key in enabled_multi_keys else "[ ]"
        subtitle_parts = [part for part in (mode_subtitle, enabled_text, clean_preview(final_prompt, 56)) if part]
        items.append(
            {
                "uid": f"single_{key}",
                "title": platform["name"],
                "subtitle": " | ".join(subtitle_parts),
                "arg": single_payload,
                "variables": {"mode": "single", "final_prompt": final_prompt},
                "icon": {"path": f"icons/{platform['icon']}"},
                "skipknowledge": True,
            }
        )

    if enabled_multi_keys:
        multi_targets = [build_open_target(key, final_prompt, autosend) for key in enabled_multi_keys]
        multi_payload = base64.urlsafe_b64encode(
            json.dumps(multi_targets, ensure_ascii=False).encode("utf-8")
        ).decode("ascii")
        display_names = " + ".join(PLATFORMS[key]["name"] for key in enabled_multi_keys)
        multi_subtitle_parts = [part for part in (mode_subtitle, clean_preview(final_prompt, 48)) if part]
        items.append(
            {
                "title": f"同时打开 {display_names}",
                "subtitle": " | ".join(multi_subtitle_parts),
                "arg": multi_payload,
                "variables": {"mode": "multi", "final_prompt": final_prompt},
                "icon": {"path": "icon.png"},
                "skipknowledge": True,
            }
        )

    return items


def build_idle_items(clipboard_content: str):
    items = []
    if clipboard_content:
        items.append(
            {
                "title": "使用剪贴板内容",
                "subtitle": clean_preview(clipboard_content, 60),
                "autocomplete": f"{clipboard_content} ",
                "icon": {"path": "icon.png"},
                "valid": False,
                "skipknowledge": True,
            }
        )

    for key, template in PROMPT_TEMPLATES.items():
        items.append(
            {
                "title": template["title"],
                "subtitle": f"{key} ⇥ Tab 补全前缀",
                "autocomplete": f"{key} ",
                "valid": False,
                "icon": {"path": "icon.png"},
                "skipknowledge": True,
            }
        )
    return items


def resolve_prompt(raw_query: str, clipboard_content: str):
    parts = raw_query.split(" ", 1)
    prefix = parts[0].lower()

    if prefix in PROMPT_TEMPLATES:
        user_input = parts[1] if len(parts) > 1 else ""
        if user_input:
            final_prompt = PROMPT_TEMPLATES[prefix]["prompt"] + user_input
            return final_prompt, PROMPT_TEMPLATES[prefix]["title"]
        if clipboard_content:
            final_prompt = PROMPT_TEMPLATES[prefix]["prompt"] + clipboard_content
            return final_prompt, f"{PROMPT_TEMPLATES[prefix]['title']} · 剪贴板"
        return "", ""

    return raw_query, ""


def main():
    raw_query = sys.argv[1] if len(sys.argv) > 1 else ""
    raw_query = raw_query.lstrip()
    clipboard_content = get_clipboard()

    if not raw_query.strip():
        json_print(build_idle_items(clipboard_content))
        return

    final_prompt, mode_subtitle = resolve_prompt(raw_query, clipboard_content)
    if not final_prompt:
        json_print(
            [
                {
                    "title": "等待内容",
                    "subtitle": "继续输入，或先复制内容到剪贴板",
                    "valid": False,
                    "icon": {"path": "icon.png"},
                    "skipknowledge": True,
                }
            ]
        )
        return

    json_print(build_platform_items(final_prompt, mode_subtitle))


if __name__ == "__main__":
    main()
