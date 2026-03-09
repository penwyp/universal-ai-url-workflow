PYTHON ?= python3

VERSION := $(shell cat version)
PACKAGE := dist/universal-ai-prompt-$(VERSION).alfredworkflow

.PHONY: all build package plist clean lint icon

all: clean icon package

build: all

package: $(PACKAGE)

plist: info.plist

icon: icon.png

info.plist: scripts/generate_info_plist.py workflow/config/workflow.json workflow/config/platforms.json version
	$(PYTHON) scripts/generate_info_plist.py

icon.png: icons/Default.icns
	sips -s format png icons/Default.icns --out icon.png >/dev/null

lint:
	$(PYTHON) -m py_compile workflow/script_filter.py workflow/open_multi.py scripts/generate_info_plist.py scripts/package_workflow.py
	plutil -lint info.plist

clean:
	rm -rf dist
	rm -rf __pycache__ workflow/__pycache__ scripts/__pycache__
	rm -f info.plist icon.png

$(PACKAGE): info.plist icon.png scripts/package_workflow.py workflow/script_filter.py workflow/open_multi.py workflow/config/templates.json workflow/config/platforms.json workflow/config/workflow.json
	$(PYTHON) scripts/package_workflow.py
