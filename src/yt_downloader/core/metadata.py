import os

from mutagen.mp4 import MP4, MP4Cover, MP4StreamInfoError

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _make_cover(cover_art_data):
    if cover_art_data.startswith(JPEG_MAGIC):
        return MP4Cover(cover_art_data, imageformat=MP4Cover.FORMAT_JPEG)
    if cover_art_data.startswith(PNG_MAGIC):
        return MP4Cover(cover_art_data, imageformat=MP4Cover.FORMAT_PNG)
    raise ValueError("Unsupported image format. Use JPEG or PNG.")


def write_metadata(filepath, title, artist="", cover_art_data=None):
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in (".mp4", ".m4a", ".m4v", ".mov"):
        return

    try:
        tags = MP4(filepath)
        tags["\xa9nam"] = [title]
        if artist:
            tags["\xa9ART"] = [artist]
        if cover_art_data:
            tags["covr"] = [_make_cover(cover_art_data)]
        tags.save()
    except MP4StreamInfoError:
        pass
