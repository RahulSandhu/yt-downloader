import os
import shutil

from PyQt5.QtCore import QDir, QThread
from PyQt5.QtWidgets import (
    QButtonGroup,
    QFileSystemModel,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from yt_downloader.core.cover_art import CoverArtWorker
from yt_downloader.core.downloader import DownloadWorker
from yt_downloader.core.metadata import write_metadata
from yt_downloader.utils.filename import to_snake


class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Downloader")
        self.setGeometry(200, 200, 500, 650)
        self.temp_filepath = None
        self.selected_save_dir = None
        self.cover_art_data = None
        self.file_extension = None
        self.download_completed = False
        self.init_ui()

    def init_ui(self):
        download_group = QGroupBox("Step 1: Download")
        download_layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste URL here (YouTube, Twitter, Instagram, TikTok, etc.)..."
        )
        download_layout.addWidget(QLabel("Enter URL:"))
        download_layout.addWidget(self.url_input)

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Download as:"))
        self.audio_radio = QRadioButton("Audio Only")
        self.video_radio = QRadioButton("Video")
        self.video_radio.setChecked(True)

        self.format_button_group = QButtonGroup()
        self.format_button_group.addButton(self.audio_radio)
        self.format_button_group.addButton(self.video_radio)

        format_layout.addWidget(self.audio_radio)
        format_layout.addWidget(self.video_radio)
        download_layout.addLayout(format_layout)

        self.download_button = QPushButton("Download")
        download_layout.addWidget(self.download_button)
        download_group.setLayout(download_layout)

        self.metadata_group = QGroupBox("Step 2: Metadata")
        metadata_layout = QVBoxLayout()

        self.title_label = QLabel("Title:")
        metadata_layout.addWidget(self.title_label)
        self.title_input = QLineEdit()
        metadata_layout.addWidget(self.title_input)

        self.artist_label = QLabel("Artist:")
        metadata_layout.addWidget(self.artist_label)
        self.artist_input = QLineEdit()
        metadata_layout.addWidget(self.artist_input)

        self.cover_art_label = QLabel("Cover art:")
        metadata_layout.addWidget(self.cover_art_label)
        cover_art_layout = QHBoxLayout()
        self.cover_yes_radio = QRadioButton("Yes")
        self.cover_no_radio = QRadioButton("No")
        self.cover_no_radio.setChecked(True)
        self.cover_button_group = QButtonGroup()
        self.cover_button_group.addButton(self.cover_yes_radio)
        self.cover_button_group.addButton(self.cover_no_radio)
        cover_art_layout.addWidget(self.cover_yes_radio)
        cover_art_layout.addWidget(self.cover_no_radio)
        cover_art_layout.addStretch()
        metadata_layout.addLayout(cover_art_layout)
        self.cover_art_note = QLabel("")
        metadata_layout.addWidget(self.cover_art_note)
        self.metadata_group.setLayout(metadata_layout)

        self.save_group = QGroupBox("Step 3: Saving")
        save_layout = QVBoxLayout()

        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.homePath())
        self.fs_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.dir_tree = QTreeView()
        self.dir_tree.setModel(self.fs_model)
        self.dir_tree.setRootIndex(self.fs_model.index(QDir.homePath()))
        self.dir_tree.hideColumn(1)
        self.dir_tree.hideColumn(2)
        self.dir_tree.hideColumn(3)

        create_folder_layout = QHBoxLayout()
        self.create_folder_button = QPushButton("Create Folder")
        create_folder_layout.addWidget(self.create_folder_button)
        create_folder_layout.addStretch()

        filename_layout = QHBoxLayout()
        self.filename_input = QLineEdit()
        self.save_button = QPushButton("Save")
        filename_layout.addWidget(QLabel("File name:"))
        filename_layout.addWidget(self.filename_input)
        filename_layout.addWidget(self.save_button)
        save_layout.addWidget(self.dir_tree)
        save_layout.addLayout(create_folder_layout)
        save_layout.addLayout(filename_layout)
        self.save_group.setLayout(save_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(download_group)
        main_layout.addWidget(self.metadata_group)
        main_layout.addWidget(self.save_group)
        self.status_label = QLabel("Status: Ready")
        main_layout.addWidget(self.status_label)
        self.setLayout(main_layout)

        self.metadata_group.setEnabled(False)
        self.save_group.setEnabled(False)

        self.download_button.clicked.connect(self.start_download)
        self.dir_tree.clicked.connect(self.on_folder_selected)
        self.save_button.clicked.connect(self.save_file)
        self.create_folder_button.clicked.connect(self.create_folder)
        self.cover_yes_radio.toggled.connect(self.on_cover_toggled)
        self.title_input.textChanged.connect(self.update_suggested_filename)
        self.audio_radio.toggled.connect(self.update_audio_fields_visibility)
        self.video_radio.toggled.connect(self.update_audio_fields_visibility)
        self.update_audio_fields_visibility()

    def on_cover_toggled(self, checked):
        if checked:
            self.search_cover_art()
        else:
            self.cover_art_data = None
            self.cover_art_note.setText("")

    def search_cover_art(self):
        artist = self.artist_input.text()
        title = self.title_input.text()
        if not artist or not title:
            QMessageBox.warning(
                self, "Warning", "Please enter both Title and Artist first."
            )
            return

        self.cover_art_note.setText("Searching cover art...")

        self.cover_thread = QThread()
        self.cover_worker = CoverArtWorker(artist, title)
        self.cover_worker.moveToThread(self.cover_thread)

        self.cover_thread.started.connect(self.cover_worker.run)
        self.cover_worker.finished.connect(self.on_cover_results)
        self.cover_worker.error.connect(self.on_cover_error)
        self.cover_worker.finished.connect(self.cover_thread.quit)
        self.cover_worker.finished.connect(self.cover_worker.deleteLater)
        self.cover_worker.error.connect(self.cover_thread.quit)
        self.cover_worker.error.connect(self.cover_worker.deleteLater)
        self.cover_thread.finished.connect(self.cover_thread.deleteLater)

        self.cover_thread.start()

    def on_cover_results(self, artist, title, data):
        if not data:
            self.cover_art_data = None
            self.cover_art_note.setText("No cover art found.")
            return
        self.cover_art_data = data
        self.cover_art_note.setText(f"Cover art: {artist} - {title}")

    def on_cover_error(self, message):
        self.cover_art_data = None
        self.cover_art_note.setText(message)

    def update_audio_fields_visibility(self):
        visible = self.audio_radio.isChecked() and self.download_completed
        self.title_label.setVisible(visible)
        self.title_input.setVisible(visible)
        self.artist_label.setVisible(visible)
        self.artist_input.setVisible(visible)
        self.cover_art_label.setVisible(visible)
        self.cover_yes_radio.setVisible(visible)
        self.cover_no_radio.setVisible(visible)
        self.cover_art_note.setVisible(visible)

    def start_download(self):
        video_url = self.url_input.text()
        if not video_url:
            return

        download_type = "audio" if self.audio_radio.isChecked() else "video"
        self.download_completed = False
        self.update_audio_fields_visibility()
        self.download_button.setEnabled(False)
        self.metadata_group.setEnabled(False)
        self.save_group.setEnabled(False)

        self.thread = QThread()
        self.worker = DownloadWorker(video_url, download_type)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.worker.progress.connect(self.update_status)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_download_finished(self, temp_filepath, suggested_filename, title, artist):
        self.temp_filepath = temp_filepath
        self.download_completed = True
        self.file_extension = os.path.splitext(suggested_filename)[1]
        self.title_input.setText(title)
        self.artist_input.setText(artist)
        self.update_audio_fields_visibility()
        self.status_label.setText("Status: Download Complete! Edit details and save.")
        self.metadata_group.setEnabled(True)
        self.save_group.setEnabled(True)

    def on_download_error(self, error_message):
        QMessageBox.critical(self, "Download Error", error_message)
        self.download_button.setEnabled(True)

    def on_folder_selected(self, index):
        self.selected_save_dir = self.fs_model.filePath(index)

    def create_folder(self):
        if not self.selected_save_dir:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        folder_name, ok = QInputDialog.getText(
            self, "Create Folder", "Enter new folder name:"
        )
        if not ok or not folder_name:
            return

        new_folder_path = os.path.join(self.selected_save_dir, folder_name)
        try:
            os.makedirs(new_folder_path, exist_ok=True)
            self.fs_model.setRootPath(self.selected_save_dir)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create folder: {e}")

    def save_file(self):
        if not self.selected_save_dir or not self.temp_filepath:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        final_filename = self.filename_input.text()
        if not final_filename:
            QMessageBox.warning(self, "Warning", "Please enter a file name.")
            return

        destination_path = os.path.join(self.selected_save_dir, final_filename)

        if self.audio_radio.isChecked():
            title = self.title_input.text()
            artist = self.artist_input.text()
            try:
                write_metadata(self.temp_filepath, title, artist, self.cover_art_data)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Metadata Warning",
                    (
                        f"Could not write metadata to the file: {e}\n\n"
                        "The file will be saved without tags."
                    ),
                )

        if os.path.exists(destination_path):
            reply = QMessageBox.question(
                self,
                "Overwrite File",
                (
                    f'A file named "{final_filename}" already exists in this'
                    " folder.\n\n"
                    "Do you want to overwrite it?"
                ),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        try:
            shutil.move(self.temp_filepath, destination_path)
            QMessageBox.information(
                self, "Success", f"Media saved to:\n{destination_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not move file: {e}")
            return

        self.reset_ui()

    def update_suggested_filename(self):
        if not self.download_completed or not self.file_extension:
            return
        title = self.title_input.text()
        if not title:
            self.filename_input.setText("")
            return
        self.filename_input.setText(to_snake(title) + self.file_extension)

    def reset_ui(self):
        self.url_input.clear()
        self.download_button.setEnabled(True)
        self.metadata_group.setEnabled(False)
        self.save_group.setEnabled(False)
        self.title_input.clear()
        self.artist_input.clear()
        self.filename_input.clear()
        self.cover_no_radio.setChecked(True)
        self.cover_art_data = None
        self.cover_art_note.setText("")
        self.file_extension = None
        self.download_completed = False
        self.update_audio_fields_visibility()
        self.status_label.setText("Status: Ready")
        self.temp_filepath = None
        self.selected_save_dir = None

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")
