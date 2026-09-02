# yt-downloader

Cross-platform media downloader GUI built with Python, PyQt5, and yt-dlp.

<p align="center">
  <img src="images/demo.png" width="800" alt="yt-downloader">
</p>

## Setup

Requires Python >= 3.14 and ffmpeg (for audio conversion).

```sh
git clone https://github.com/RahulSandhu/yt-downloader.git
cd yt-downloader
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the application during development:

```sh
make run
```

Equivalent to:

```sh
PYTHONPATH=src .venv/bin/python -m yt_downloader.main
```

Paste a URL (YouTube, Twitter, Instagram, TikTok, etc.), choose audio-only or
video, edit the title and artist and optionally fetch cover art, then pick a
destination folder and file name to save. Audio is saved as `m4a`, video as
`mp4`.
