PYTHON = .venv/bin/python
RUFF   = .venv/bin/ruff
PYINSTALLER = .venv/bin/pyinstaller

RELEASE_DIR = dist/release
ARCHIVE = $(RELEASE_DIR)/yt-downloader-linux-x86_64.tar.gz

export PYTHONPATH = src

.PHONY: help all run build clean ruff

help:
	@echo "Available targets:"
	@echo " make help  - Show available targets"
	@echo " make all   - Run ruff + build"
	@echo " make run   - Run the application"
	@echo " make build - Build standalone executable and release archive"
	@echo " make clean - Remove build artifacts and caches"
	@echo " make ruff  - Lint code with ruff"

all: clean ruff build

run:
	$(PYTHON) -m yt_downloader.main

build:
	$(PYINSTALLER) main.spec
	mkdir -p $(RELEASE_DIR)
	mv dist/yt-downloader $(RELEASE_DIR)/yt-downloader
	tar czvf $(ARCHIVE) -C $(RELEASE_DIR) yt-downloader

clean:
	rm -rf build/ dist/ src/*.egg-info .ruff_cache/

ruff:
	$(RUFF) check .
