import re


def to_snake(s):
    s = s.lower().strip()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def make_filename(info, file_extension):
    title = info.get("title") or "unknown"
    title_part = to_snake(title)
    return f"{title_part}.{file_extension}"
