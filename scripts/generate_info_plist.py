#!/usr/bin/env python3
import json
import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "workflow" / "config"
WORKFLOW = json.loads((CONFIG_DIR / "workflow.json").read_text(encoding="utf-8"))
PLATFORMS = json.loads((CONFIG_DIR / "platforms.json").read_text(encoding="utf-8"))
VERSION_FILE = ROOT / "version"
INFO_PLIST = ROOT / "info.plist"

SCRIPT_FILTER_UID = "3C36404E-52AD-4EDA-BF07-F48212F037AA"
SCRIPT_FILTER_ALIAS_UID = "A4E95F8A-C936-4CF2-A09A-6D90D4187F9A"
CLIPBOARD_UID = "C6A6A36C-5D4C-4557-B528-4E20F7E20D33"
CONDITIONAL_UID = "4F71C10B-D2A7-47CF-8C38-E4CD7639E4EA"
OPEN_URL_UID = "270A4A7C-26DB-4492-AE4E-212124822D4D"
OPEN_MULTI_UID = "60952F75-8FEA-446B-AB3B-90C260D35ABC"
SINGLE_OUTPUT_UID = "5D78157B-522D-4846-B1A3-FD8F11BEBF82"
MULTI_OUTPUT_UID = "C5A1D787-3680-4C32-82AA-7385D4AB3F3A"


def workflow_variables():
    variables = {"autosend": "1"}
    for key, platform in PLATFORMS.items():
        variables[f"enable_{key}"] = "1" if platform.get("enabled_by_default", True) else "0"
        variables[f"url_{key}"] = platform["url"]
        variables[f"browser_{key}"] = platform.get("browser_app", "")
    return variables


def workflow_keywords():
    keywords = WORKFLOW.get("keywords")
    if keywords:
        return keywords
    return [WORKFLOW["keyword"]]


def script_filter_object(uid: str, keyword: str):
    return {
        "config": {
            "alfredfiltersresults": False,
            "alfredfiltersresultsmatchmode": 0,
            "argumenttrimmode": 0,
            "argumenttype": 1,
            "escaping": 102,
            "keyword": keyword,
            "queuedelaycustom": 1,
            "queuedelayimmediatelyinitially": True,
            "queuedelaymode": 1,
            "queuemode": 1,
            "runningsubtext": WORKFLOW["script_filter_running_subtext"],
            "script": "/usr/bin/python3 ./workflow/script_filter.py \"$1\"",
            "scriptargtype": 1,
            "scriptfile": "",
            "subtext": WORKFLOW["script_filter_subtext"],
            "title": WORKFLOW["script_filter_title"],
            "type": 0,
            "withspace": True,
        },
        "type": "alfred.workflow.input.scriptfilter",
        "uid": uid,
        "version": 2,
    }


def clipboard_object():
    return {
        "config": {
            "autopaste": False,
            "clipboardtext": "{var:final_prompt}",
            "ignoredynamicplaceholders": False,
            "transient": False,
        },
        "type": "alfred.workflow.output.clipboard",
        "uid": CLIPBOARD_UID,
        "version": 3,
    }


def conditional_object():
    return {
        "config": {
            "conditions": [
                {
                    "inputstring": "{var:mode}",
                    "matchcasesensitive": False,
                    "matchmode": 0,
                    "matchstring": "single",
                    "outputlabel": "single",
                    "uid": SINGLE_OUTPUT_UID,
                },
                {
                    "inputstring": "{var:mode}",
                    "matchcasesensitive": False,
                    "matchmode": 0,
                    "matchstring": "multi",
                    "outputlabel": "multi",
                    "uid": MULTI_OUTPUT_UID,
                },
            ],
            "elselabel": "else",
        },
        "type": "alfred.workflow.utility.conditional",
        "uid": CONDITIONAL_UID,
        "version": 1,
    }


def open_multi_object():
    return {
        "config": {
            "concurrently": False,
            "escaping": 102,
            "script": "/usr/bin/python3 ./workflow/open_multi.py \"$1\"",
            "scriptargtype": 1,
            "scriptfile": "",
            "type": 0,
        },
        "type": "alfred.workflow.action.script",
        "uid": OPEN_MULTI_UID,
        "version": 2,
    }


def build_info():
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    keywords = workflow_keywords()
    script_filter_uids = [SCRIPT_FILTER_UID, SCRIPT_FILTER_ALIAS_UID]
    script_filters = [
        script_filter_object(uid, keyword)
        for uid, keyword in zip(script_filter_uids, keywords)
    ]
    connections = {
        CLIPBOARD_UID: [{"destinationuid": CONDITIONAL_UID, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
        CONDITIONAL_UID: [
            {"destinationuid": OPEN_MULTI_UID, "modifiers": 0, "modifiersubtext": "", "sourceoutputuid": SINGLE_OUTPUT_UID, "vitoclose": False},
            {"destinationuid": OPEN_MULTI_UID, "modifiers": 0, "modifiersubtext": "", "sourceoutputuid": MULTI_OUTPUT_UID, "vitoclose": False},
        ],
    }
    uidata = {
        SCRIPT_FILTER_UID: {"xpos": 80, "ypos": 140},
        SCRIPT_FILTER_ALIAS_UID: {"xpos": 80, "ypos": 220},
        CLIPBOARD_UID: {"xpos": 360, "ypos": 180},
        CONDITIONAL_UID: {"xpos": 620, "ypos": 180},
        OPEN_MULTI_UID: {"xpos": 920, "ypos": 250},
    }
    for uid in script_filter_uids[: len(script_filters)]:
        connections[uid] = [{"destinationuid": CLIPBOARD_UID, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}]
    return {
        "bundleid": WORKFLOW["bundleid"],
        "category": WORKFLOW["category"],
        "connections": connections,
        "createdby": WORKFLOW["createdby"],
        "description": WORKFLOW["description"],
        "disabled": False,
        "name": WORKFLOW["name"],
        "objects": script_filters + [clipboard_object(), conditional_object(), open_multi_object()],
        "readme": WORKFLOW["description"],
        "uidata": uidata,
        "variables": workflow_variables(),
        "version": version,
        "webaddress": WORKFLOW.get("webaddress", ""),
    }


def main():
    with INFO_PLIST.open("wb") as handle:
        plistlib.dump(build_info(), handle, sort_keys=False)
    print(INFO_PLIST)


if __name__ == "__main__":
    main()
