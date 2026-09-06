import os
import shutil
import subprocess
import sys
import tempfile

import yt_dlp
from PyQt5.QtCore import QObject, pyqtSignal

from yt_downloader.config import (
    AUDIO_EXTENSION,
    AUDIO_FORMAT,
    COOKIES_FROM_BROWSER,
    REMOTE_COMPONENTS,
    SUPPORTED_EXTENSIONS,
    VIDEO_EXTENSION,
    VIDEO_FORMAT,
)
from yt_downloader.utils.filename import make_filename


def _find_executable(name):
    candidates = [
        os.path.join(sys.prefix, "bin", name),
        os.path.expanduser("~/.local/bin/") + name,
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    system_path = shutil.which(name)
    if system_path:
        return system_path
    return None


def _convert_to_m4a(source_path, dest_path):
    ffmpeg = _find_executable("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg.")
    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i", source_path,
            "-vn",
            "-c:a", "aac",
            "-b:a", "192k",
            dest_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")


class DownloadWorker(QObject):
    finished = pyqtSignal(str, str, str, str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, url, download_type):
        super().__init__()
        self.url = url
        self.download_type = download_type

    def run(self):
        temp_dir = tempfile.gettempdir()

        if self.download_type == "audio":
            format_string = AUDIO_FORMAT
            file_extension = AUDIO_EXTENSION
        else:
            format_string = VIDEO_FORMAT
            file_extension = VIDEO_EXTENSION

        ydl_opts = {
            "format": format_string,
            "noplaylist": True,
            "outtmpl": os.path.join(temp_dir, "%(title)s [%(id)s].%(ext)s"),
        }

        if COOKIES_FROM_BROWSER:
            ydl_opts["cookiesfrombrowser"] = COOKIES_FROM_BROWSER

        if REMOTE_COMPONENTS:
            ydl_opts["remote_components"] = REMOTE_COMPONENTS

        if self.download_type == "video":
            ydl_opts["merge_output_format"] = "mp4"

        try:
            self.progress.emit("Fetching video info...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                temp_filepath = ydl.prepare_filename(info)
                suggested_filename = make_filename(info, file_extension)

                self.progress.emit(f"Downloading: {info.get('title', 'N/A')}")
                ydl.process_ie_result(info, download=True)

                actual_filepath = None
                for ext in SUPPORTED_EXTENSIONS:
                    potential_path = os.path.splitext(temp_filepath)[0] + f".{ext}"
                    if os.path.exists(potential_path):
                        actual_filepath = potential_path
                        break

                if not actual_filepath or not os.path.exists(actual_filepath):
                    self.error.emit("Downloaded file could not be found.")
                    return

                if self.download_type == "audio":
                    actual_ext = os.path.splitext(actual_filepath)[1].lower()
                    if actual_ext != ".m4a":
                        self.progress.emit("Converting to m4a...")
                        converted_path = os.path.splitext(actual_filepath)[0] + ".m4a"
                        _convert_to_m4a(actual_filepath, converted_path)
                        os.remove(actual_filepath)
                        actual_filepath = converted_path

                extracted_title = info.get("title", "")
                extracted_artist = (
                    info.get("artist")
                    or info.get("creator")
                    or info.get("uploader")
                    or ""
                )

                self.finished.emit(
                    actual_filepath,
                    suggested_filename,
                    extracted_title,
                    extracted_artist,
                )
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
