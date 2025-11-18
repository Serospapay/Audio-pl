"""
Вікно редагування метаданих аудіофайлів
"""
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTextEdit, QMessageBox, QFormLayout, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2, TDRC, TCON, COMM
from mutagen.id3 import ID3NoHeaderError
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MetadataEditor(QDialog):
    """Діалог редагування метаданих аудіофайлу"""
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self._file_path = file_path
        self._audio_file = None
        self._file_type = None
        
        self.setWindowTitle(f"Редагування метаданих - {Path(file_path).name}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self._init_ui()
        self._load_metadata()
    
    def _init_ui(self):
        """Ініціалізація UI"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("Редагування метаданих")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Форма з полями
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)
        
        # Назва треку
        self._title_edit = QLineEdit()
        form_layout.addRow("Назва треку:", self._title_edit)
        
        # Виконавець
        self._artist_edit = QLineEdit()
        form_layout.addRow("Виконавець:", self._artist_edit)
        
        # Альбом
        self._album_edit = QLineEdit()
        form_layout.addRow("Альбом:", self._album_edit)
        
        # Виконавець альбому
        self._album_artist_edit = QLineEdit()
        form_layout.addRow("Виконавець альбому:", self._album_artist_edit)
        
        # Рік
        self._year_edit = QLineEdit()
        form_layout.addRow("Рік:", self._year_edit)
        
        # Жанр
        self._genre_edit = QLineEdit()
        form_layout.addRow("Жанр:", self._genre_edit)
        
        # Коментар
        self._comment_edit = QTextEdit()
        self._comment_edit.setMaximumHeight(80)
        form_layout.addRow("Коментар:", self._comment_edit)
        
        layout.addWidget(form_widget)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self._save_metadata)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_metadata(self):
        """Завантажує метадані з файлу"""
        try:
            self._audio_file = MutagenFile(self._file_path)
            if self._audio_file is None:
                QMessageBox.warning(self, "Помилка", "Не вдалося відкрити файл")
                return
            
            # Визначаємо тип файлу
            file_ext = Path(self._file_path).suffix.lower()
            if file_ext in ['.mp3']:
                self._file_type = 'mp3'
            elif file_ext in ['.m4a', '.mp4', '.aac']:
                self._file_type = 'm4a'
            elif file_ext in ['.flac']:
                self._file_type = 'flac'
            else:
                self._file_type = 'other'
            
            # Завантажуємо метадані
            if self._file_type == 'mp3':
                self._load_mp3_metadata()
            elif self._file_type == 'm4a':
                self._load_m4a_metadata()
            elif self._file_type == 'flac':
                self._load_flac_metadata()
            else:
                self._load_generic_metadata()
                
        except Exception as e:
            logger.error(f"Помилка завантаження метаданих: {e}", exc_info=True)
            QMessageBox.warning(self, "Помилка", f"Не вдалося завантажити метадані: {str(e)}")
    
    def _load_mp3_metadata(self):
        """Завантажує метадані MP3"""
        try:
            if not self._audio_file.tags:
                # Створюємо нові теги якщо немає
                self._audio_file.add_tags()
            
            tags = self._audio_file.tags
            
            # TIT2 - Title
            if 'TIT2' in tags:
                self._title_edit.setText(str(tags['TIT2'][0]))
            
            # TPE1 - Artist
            if 'TPE1' in tags:
                self._artist_edit.setText(str(tags['TPE1'][0]))
            
            # TALB - Album
            if 'TALB' in tags:
                self._album_edit.setText(str(tags['TALB'][0]))
            
            # TPE2 - Album Artist
            if 'TPE2' in tags:
                self._album_artist_edit.setText(str(tags['TPE2'][0]))
            
            # TDRC - Year
            if 'TDRC' in tags:
                year = str(tags['TDRC'][0])
                # Може бути дата, беремо рік
                if len(year) >= 4:
                    self._year_edit.setText(year[:4])
            
            # TCON - Genre
            if 'TCON' in tags:
                self._genre_edit.setText(str(tags['TCON'][0]))
            
            # COMM - Comment
            if 'COMM::eng' in tags:
                self._comment_edit.setPlainText(str(tags['COMM::eng'][0]))
            elif 'COMM' in tags:
                self._comment_edit.setPlainText(str(tags['COMM'][0]))
                
        except ID3NoHeaderError:
            # Файл без ID3 тегів, створюємо нові
            self._audio_file.add_tags()
        except Exception as e:
            logger.error(f"Помилка завантаження MP3 метаданих: {e}", exc_info=True)
    
    def _load_m4a_metadata(self):
        """Завантажує метадані M4A"""
        try:
            tags = self._audio_file.tags
            
            # \xa9nam - Title
            if '\xa9nam' in tags:
                self._title_edit.setText(str(tags['\xa9nam'][0]))
            
            # \xa9ART - Artist
            if '\xa9ART' in tags:
                self._artist_edit.setText(str(tags['\xa9ART'][0]))
            
            # \xa9alb - Album
            if '\xa9alb' in tags:
                self._album_edit.setText(str(tags['\xa9alb'][0]))
            
            # aART - Album Artist
            if 'aART' in tags:
                self._album_artist_edit.setText(str(tags['aART'][0]))
            
            # \xa9day - Year
            if '\xa9day' in tags:
                year = str(tags['\xa9day'][0])
                if len(year) >= 4:
                    self._year_edit.setText(year[:4])
            
            # \xa9gen - Genre
            if '\xa9gen' in tags:
                self._genre_edit.setText(str(tags['\xa9gen'][0]))
                
        except Exception as e:
            logger.error(f"Помилка завантаження M4A метаданих: {e}", exc_info=True)
    
    def _load_flac_metadata(self):
        """Завантажує метадані FLAC"""
        try:
            tags = self._audio_file
            
            if 'TITLE' in tags:
                self._title_edit.setText(str(tags['TITLE'][0]))
            
            if 'ARTIST' in tags:
                self._artist_edit.setText(str(tags['ARTIST'][0]))
            
            if 'ALBUM' in tags:
                self._album_edit.setText(str(tags['ALBUM'][0]))
            
            if 'ALBUMARTIST' in tags:
                self._album_artist_edit.setText(str(tags['ALBUMARTIST'][0]))
            
            if 'DATE' in tags:
                year = str(tags['DATE'][0])
                if len(year) >= 4:
                    self._year_edit.setText(year[:4])
            
            if 'GENRE' in tags:
                self._genre_edit.setText(str(tags['GENRE'][0]))
            
            if 'COMMENT' in tags:
                self._comment_edit.setPlainText(str(tags['COMMENT'][0]))
                
        except Exception as e:
            logger.error(f"Помилка завантаження FLAC метаданих: {e}", exc_info=True)
    
    def _load_generic_metadata(self):
        """Завантажує метадані для інших форматів"""
        try:
            tags = self._audio_file
            
            if 'TITLE' in tags:
                self._title_edit.setText(str(tags['TITLE'][0]))
            
            if 'ARTIST' in tags:
                self._artist_edit.setText(str(tags['ARTIST'][0]))
            
            if 'ALBUM' in tags:
                self._album_edit.setText(str(tags['ALBUM'][0]))
                
        except Exception as e:
            logger.error(f"Помилка завантаження метаданих: {e}", exc_info=True)
    
    def _save_metadata(self):
        """Зберігає метадані у файл"""
        try:
            if self._file_type == 'mp3':
                self._save_mp3_metadata()
            elif self._file_type == 'm4a':
                self._save_m4a_metadata()
            elif self._file_type == 'flac':
                self._save_flac_metadata()
            else:
                QMessageBox.warning(self, "Помилка", "Редагування метаданих для цього формату не підтримується")
                return
            
            # Зберігаємо файл
            self._audio_file.save()
            
            QMessageBox.information(self, "Успіх", "Метадані збережено успішно")
            self.accept()
            
        except Exception as e:
            logger.error(f"Помилка збереження метаданих: {e}", exc_info=True)
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти метадані: {str(e)}")
    
    def _save_mp3_metadata(self):
        """Зберігає метадані MP3"""
        try:
            if not self._audio_file.tags:
                self._audio_file.add_tags()
            
            tags = self._audio_file.tags
            
            # Очищаємо старі теги
            if 'TIT2' in tags:
                del tags['TIT2']
            if 'TPE1' in tags:
                del tags['TPE1']
            if 'TALB' in tags:
                del tags['TALB']
            if 'TPE2' in tags:
                del tags['TPE2']
            if 'TDRC' in tags:
                del tags['TDRC']
            if 'TCON' in tags:
                del tags['TCON']
            if 'COMM::eng' in tags:
                del tags['COMM::eng']
            if 'COMM' in tags:
                del tags['COMM']
            
            # Додаємо нові теги
            if self._title_edit.text().strip():
                tags['TIT2'] = TIT2(encoding=3, text=self._title_edit.text().strip())
            
            if self._artist_edit.text().strip():
                tags['TPE1'] = TPE1(encoding=3, text=self._artist_edit.text().strip())
            
            if self._album_edit.text().strip():
                tags['TALB'] = TALB(encoding=3, text=self._album_edit.text().strip())
            
            if self._album_artist_edit.text().strip():
                tags['TPE2'] = TPE2(encoding=3, text=self._album_artist_edit.text().strip())
            
            if self._year_edit.text().strip():
                tags['TDRC'] = TDRC(encoding=3, text=self._year_edit.text().strip())
            
            if self._genre_edit.text().strip():
                tags['TCON'] = TCON(encoding=3, text=self._genre_edit.text().strip())
            
            if self._comment_edit.toPlainText().strip():
                tags['COMM::eng'] = COMM(encoding=3, lang='eng', desc='', text=self._comment_edit.toPlainText().strip())
                
        except Exception as e:
            logger.error(f"Помилка збереження MP3 метаданих: {e}", exc_info=True)
            raise
    
    def _save_m4a_metadata(self):
        """Зберігає метадані M4A"""
        try:
            tags = self._audio_file.tags
            
            # Очищаємо старі теги
            for key in ['\xa9nam', '\xa9ART', '\xa9alb', 'aART', '\xa9day', '\xa9gen']:
                if key in tags:
                    del tags[key]
            
            # Додаємо нові теги
            if self._title_edit.text().strip():
                tags['\xa9nam'] = [self._title_edit.text().strip()]
            
            if self._artist_edit.text().strip():
                tags['\xa9ART'] = [self._artist_edit.text().strip()]
            
            if self._album_edit.text().strip():
                tags['\xa9alb'] = [self._album_edit.text().strip()]
            
            if self._album_artist_edit.text().strip():
                tags['aART'] = [self._album_artist_edit.text().strip()]
            
            if self._year_edit.text().strip():
                tags['\xa9day'] = [self._year_edit.text().strip()]
            
            if self._genre_edit.text().strip():
                tags['\xa9gen'] = [self._genre_edit.text().strip()]
                
        except Exception as e:
            logger.error(f"Помилка збереження M4A метаданих: {e}", exc_info=True)
            raise
    
    def _save_flac_metadata(self):
        """Зберігає метадані FLAC"""
        try:
            tags = self._audio_file
            
            # Очищаємо старі теги
            for key in ['TITLE', 'ARTIST', 'ALBUM', 'ALBUMARTIST', 'DATE', 'GENRE', 'COMMENT']:
                if key in tags:
                    del tags[key]
            
            # Додаємо нові теги
            if self._title_edit.text().strip():
                tags['TITLE'] = [self._title_edit.text().strip()]
            
            if self._artist_edit.text().strip():
                tags['ARTIST'] = [self._artist_edit.text().strip()]
            
            if self._album_edit.text().strip():
                tags['ALBUM'] = [self._album_edit.text().strip()]
            
            if self._album_artist_edit.text().strip():
                tags['ALBUMARTIST'] = [self._album_artist_edit.text().strip()]
            
            if self._year_edit.text().strip():
                tags['DATE'] = [self._year_edit.text().strip()]
            
            if self._genre_edit.text().strip():
                tags['GENRE'] = [self._genre_edit.text().strip()]
            
            if self._comment_edit.toPlainText().strip():
                tags['COMMENT'] = [self._comment_edit.toPlainText().strip()]
                
        except Exception as e:
            logger.error(f"Помилка збереження FLAC метаданих: {e}", exc_info=True)
            raise

