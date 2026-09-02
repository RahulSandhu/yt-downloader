# Changelog

## [0.1.0]

First release of yt-downloader.

Cross-platform media downloader GUI built with Python, PyQt5, and yt-dlp.

- PyQt5 desktop GUI for downloading media from yt-dlp supported sites.
- Download audio or video from a pasted URL.
- Audio conversion to `m4a` (AAC 192 kbps) via ffmpeg.
- Video downloads merged to `mp4`.
- Edit title and artist metadata on downloaded audio files.
- Optional cover art fetching from the iTunes Search API, embedded as JPEG/PNG
  in the output file.
- Browser cookie support for authenticated downloads.
- Configurable download formats, extensions, and remote components in
  `src/yt_downloader/config.py`.
- PyInstaller build configuration (`main.spec`) and release archive target.
