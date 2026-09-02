import requests
from PyQt5.QtCore import QObject, pyqtSignal

SEARCH_URL = "https://itunes.apple.com/search"


def search_covers(artist, title):
    if not artist or not title:
        return []
    term = f"{artist} {title}"
    response = requests.get(
        SEARCH_URL,
        params={"term": term, "entity": "song", "limit": 15},
        timeout=15,
    )
    response.raise_for_status()
    results = response.json().get("results", [])

    seen = set()
    covers = []
    for r in results:
        url = r.get("artworkUrl100")
        if not url or url in seen:
            continue
        seen.add(url)
        covers.append(
            {
                "artist": r.get("artistName", ""),
                "title": r.get("trackName", ""),
                "url": url.replace("100x100", "1200x1200"),
            }
        )
        if len(covers) >= 3:
            break
    return covers


def download_cover(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.content


class CoverArtWorker(QObject):
    finished = pyqtSignal(str, str, bytes)
    error = pyqtSignal(str)

    def __init__(self, artist, title):
        super().__init__()
        self.artist = artist
        self.title = title

    def run(self):
        try:
            covers = search_covers(self.artist, self.title)
            if not covers:
                self.finished.emit("", "", b"")
                return
            best = covers[0]
            data = download_cover(best["url"])
            self.finished.emit(best["artist"], best["title"], data)
        except Exception as e:
            self.error.emit(f"Error fetching cover art: {e}")
