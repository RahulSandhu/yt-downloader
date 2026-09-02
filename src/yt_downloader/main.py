import sys

from PyQt5.QtWidgets import QApplication

from yt_downloader.ui.main_window import DownloaderApp

def main():
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
