import os

SUPPORTED_EXTENSIONS = ["m4a", "webm", "mkv", "mp4"]

AUDIO_FORMAT = "bestaudio/best"
VIDEO_FORMAT = "bestvideo*+bestaudio/best"

AUDIO_EXTENSION = "m4a"
VIDEO_EXTENSION = "mp4"

COOKIES_BROWSER = os.environ.get("YT_DOWNLOADER_COOKIES_BROWSER", "firefox")
COOKIES_PROFILE = os.environ.get("YT_DOWNLOADER_COOKIES_PROFILE")

COOKIES_FROM_BROWSER = (
    (COOKIES_BROWSER, COOKIES_PROFILE) if COOKIES_PROFILE else COOKIES_BROWSER
)

REMOTE_COMPONENTS = {"ejs:github", "ejs:npm"}
