"""
Вікно налаштувань
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSpinBox, QCheckBox, QGroupBox, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SettingsDialog(QDialog):
    """Діалогове вікно налаштувань"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Налаштування")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Ініціалізація UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Група "Відтворення"
        playback_group = QGroupBox("Відтворення")
        playback_layout = QVBoxLayout()
        
        # Автозапуск
        self._autoplay_checkbox = QCheckBox("Автоматично відтворювати при запуску")
        playback_layout.addWidget(self._autoplay_checkbox)
        
        # Автопродовження
        self._resume_checkbox = QCheckBox("Продовжувати відтворення з збереженої позиції")
        playback_layout.addWidget(self._resume_checkbox)
        
        playback_group.setLayout(playback_layout)
        layout.addWidget(playback_group)
        
        # Група "Інтерфейс"
        ui_group = QGroupBox("Інтерфейс")
        ui_layout = QVBoxLayout()
        
        # Розмір обкладинки
        artwork_layout = QHBoxLayout()
        artwork_label = QLabel("Розмір обкладинки альбому:")
        artwork_layout.addWidget(artwork_label)
        self._artwork_size_spinbox = QSpinBox()
        self._artwork_size_spinbox.setMinimum(100)
        self._artwork_size_spinbox.setMaximum(300)
        self._artwork_size_spinbox.setValue(150)
        self._artwork_size_spinbox.setSuffix(" px")
        artwork_layout.addWidget(self._artwork_size_spinbox)
        artwork_layout.addStretch()
        ui_layout.addLayout(artwork_layout)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Група "Плейлист"
        playlist_group = QGroupBox("Плейлист")
        playlist_layout = QVBoxLayout()
        
        # Автозбереження
        self._autosave_checkbox = QCheckBox("Автоматично зберігати плейлист при закритті")
        playlist_layout.addWidget(self._autosave_checkbox)
        
        playlist_group.setLayout(playlist_layout)
        layout.addWidget(playlist_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self._ok_button = QPushButton("OK")
        self._ok_button.clicked.connect(self._save_and_close)
        buttons_layout.addWidget(self._ok_button)
        
        self._cancel_button = QPushButton("Скасувати")
        self._cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self._cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def _load_settings(self):
        """Завантажує поточні налаштування"""
        try:
            import json
            from pathlib import Path
            
            settings_file = Path(__file__).parent.parent.parent / "settings.json"
            
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self._autoplay_checkbox.setChecked(settings.get('autoplay', False))
                self._resume_checkbox.setChecked(settings.get('resume', True))
                self._artwork_size_spinbox.setValue(settings.get('artwork_size', 150))
                self._autosave_checkbox.setChecked(settings.get('autosave', True))
            else:
                # Значення за замовчуванням
                self._autoplay_checkbox.setChecked(False)
                self._resume_checkbox.setChecked(True)
                self._artwork_size_spinbox.setValue(150)
                self._autosave_checkbox.setChecked(True)
        except Exception as e:
            logger.error(f"Помилка завантаження налаштувань: {e}", exc_info=True)
    
    def _save_and_close(self):
        """Зберігає налаштування та закриває вікно"""
        try:
            from pathlib import Path
            import json
            
            settings = {
                'autoplay': self._autoplay_checkbox.isChecked(),
                'resume': self._resume_checkbox.isChecked(),
                'artwork_size': self._artwork_size_spinbox.value(),
                'autosave': self._autosave_checkbox.isChecked()
            }
            
            settings_file = Path(__file__).parent.parent.parent / "settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            logger.info("Налаштування збережено")
            self.accept()
        except Exception as e:
            logger.error(f"Помилка збереження налаштувань: {e}", exc_info=True)
            self.reject()
    
    def get_settings(self) -> dict:
        """Повертає поточні налаштування"""
        return {
            'autoplay': self._autoplay_checkbox.isChecked(),
            'resume': self._resume_checkbox.isChecked(),
            'artwork_size': self._artwork_size_spinbox.value(),
            'autosave': self._autosave_checkbox.isChecked()
        }

