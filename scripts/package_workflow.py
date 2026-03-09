#!/usr/bin/env python3
import importlib.util
import plistlib
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist"
INCLUDE_PATHS = [
    ROOT / "info.plist",
    ROOT / "icon.png",
    ROOT / "README.md",
    ROOT / "version",
    ROOT / "workflow",
    ROOT / "icons",
]
EXCLUDE_NAMES = {"__pycache__", ".DS_Store", "README.md"}


def safe_name(text: str) -> str:
    text = text.strip().lower().replace(" ", "-")
    text = re.sub(r"[^a-z0-9.-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "workflow"


def iter_files(path: Path):
    if path.is_file():
        yield path
        return
    for item in sorted(path.rglob("*")):
        if item.is_dir() or item.name in EXCLUDE_NAMES:
            continue
        yield item


def generate_info_plist():
    generator_path = ROOT / "scripts" / "generate_info_plist.py"
    spec = importlib.util.spec_from_file_location("generate_info_plist", generator_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.main()


def main():
    generate_info_plist()
    DIST_DIR.mkdir(exist_ok=True)
    info = plistlib.loads((ROOT / "info.plist").read_bytes())
    filename = f"{safe_name(info['name'])}-{info['version']}.alfredworkflow"
    output = DIST_DIR / filename

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in INCLUDE_PATHS:
            for file in iter_files(path):
                archive.write(file, file.relative_to(ROOT))

    print(output)


if __name__ == "__main__":
    main()
