import sys
import os
import pygame
import eyed3
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QSlider, QTreeWidget, QTreeWidgetItem, QMenuBar, QLabel, QProgressBar

pygame.mixer.init()

class Mp3Player(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MP3 Player")
        self.setGeometry(100, 100, 800, 450)

        self.is_playing = False
        self.current_song = ""
        self.song_duration = 0
        self.folder_path = ""
        self.current_position = 0

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        self.song_treeview = QTreeWidget(self)
        self.song_treeview.setColumnCount(4)
        self.song_treeview.setHeaderLabels(["Исполнитель", "Название песни", "Длительность", "Размер"])
        self.song_treeview.setColumnWidth(0, 200)
        self.song_treeview.setColumnWidth(1, 300)
        self.song_treeview.setColumnWidth(2, 100)
        self.song_treeview.setColumnWidth(3, 100)

        play_button = QPushButton("Play", self)
        play_button.clicked.connect(self.toggle_play)

        prev_button = QPushButton("Previous", self)
        prev_button.clicked.connect(self.play_previous)

        next_button = QPushButton("Next", self)
        next_button.clicked.connect(self.play_next)

        volume_slider = QSlider(Qt.Orientation.Horizontal, self)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.valueChanged.connect(self.set_volume)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(play_button)
        button_layout.addWidget(next_button)

        layout = QVBoxLayout(main_widget)
        layout.addWidget(self.song_treeview)
        layout.addLayout(button_layout)
        layout.addWidget(volume_slider)
        layout.addWidget(self.progress_bar)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(1000)

    def get_song_info(self, file_path):
        try:
            audiofile = eyed3.load(file_path)
            artist = audiofile.tag.artist if audiofile.tag.artist else "Unknown Artist"
            title = audiofile.tag.title if audiofile.tag.title else os.path.basename(file_path)
            duration = int(audiofile.info.time_secs)
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
        except Exception as e:
            artist = "Unknown Artist"
            title = os.path.basename(file_path)
            duration_str = "N/A"

        file_size = os.path.getsize(file_path)
        file_size_kb = file_size // 1024
        file_size_mb = file_size_kb // 1024
        file_size_str = f"{file_size_mb} MB"

        return artist, title, duration_str, file_size_str, duration

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку с музыкой")
        if folder_path:
            self.folder_path = folder_path
            self.song_treeview.clear()

            for file_name in os.listdir(folder_path):
                if file_name.endswith('.mp3'):
                    file_path = os.path.join(folder_path, file_name)
                    artist, title = self.split_artist_title(file_name)
                    duration, size = self.get_song_info(file_path)[2:4]
                    item = QTreeWidgetItem(self.song_treeview)
                    item.setText(0, artist)
                    item.setText(1, title)
                    item.setText(2, duration)
                    item.setText(3, size)
                    item.setData(0, Qt.ItemDataRole.UserRole, file_path)

    def split_artist_title(self, file_name):
        if '-' in file_name:
            artist, title = file_name.split('-', 1)
        else:
            artist = "Unknown Artist"
            title = file_name
        return artist, title

    def toggle_play(self):
        selected_item = self.song_treeview.selectedItems()
        if selected_item:
            selected_item = selected_item[0]
            selected_file_path = selected_item.data(0, Qt.ItemDataRole.UserRole)

            if not self.is_playing:
                try:
                    if selected_item.text(1) != self.current_song:
                        self.current_song = selected_item.text(1)
                        pygame.mixer.music.load(selected_file_path)
                        pygame.mixer.music.play()

                        self.song_duration = self.get_song_info(selected_file_path)[4]
                        self.progress_bar.setRange(0, self.song_duration)

                    else:
                        pygame.mixer.music.unpause()

                    self.is_playing = True
                except Exception as e:
                    print(f"Ошибка воспроизведения: {e}")
            else:
                pygame.mixer.music.pause()
                self.is_playing = False

    def play_previous(self):
        selected_item = self.song_treeview.selectedItems()
        if selected_item:
            current_index = self.song_treeview.indexOfTopLevelItem(selected_item[0])
            if current_index > 0:
                prev_item = self.song_treeview.topLevelItem(current_index - 1)
                self.song_treeview.setCurrentItem(prev_item)
                self.toggle_play()

    def play_next(self):
        selected_item = self.song_treeview.selectedItems()
        if selected_item:
            current_index = self.song_treeview.indexOfTopLevelItem(selected_item[0])
            if current_index < self.song_treeview.topLevelItemCount() - 1:
                next_item = self.song_treeview.topLevelItem(current_index + 1)
                self.song_treeview.setCurrentItem(next_item)
                self.toggle_play()

    def set_volume(self, value):
        volume = value / 100
        pygame.mixer.music.set_volume(volume)

    def update_progress(self):
        if self.is_playing:
            self.current_position = pygame.mixer.music.get_pos() // 1000
            self.progress_bar.setValue(self.current_position)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Mp3Player()
    window.show()
    sys.exit(app.exec())
