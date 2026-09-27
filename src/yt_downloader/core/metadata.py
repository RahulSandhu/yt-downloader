import os

from mutagen.mp4 import MP4, MP4StreamInfoError


def write_metadata(filepath, title, artist=""):
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in (".mp4", ".m4a", ".m4v", ".mov"):
        return

    try:
        tags = MP4(filepath)
        tags["\xa9nam"] = [title]
        if artist:
            tags["\xa9ART"] = [artist]
        tags.save()
    except MP4StreamInfoError:
        pass
