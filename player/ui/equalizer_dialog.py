"""
Діалог еквалайзера
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QWidget, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..utils.logger import get_logger
from ..utils.state_manager import STATE_FILE
from pathlib import Path
import json

logger = get_logger(__name__)

# Частоти еквалайзера (Гц)
EQ_BANDS = [
    (60, "60 Hz"),
    (170, "170 Hz"),
    (310, "310 Hz"),
    (600, "600 Hz"),
    (1000, "1 kHz"),
    (3000, "3 kHz"),
    (6000, "6 kHz"),
    (12000, "12 kHz"),
    (14000, "14 kHz"),
    (16000, "16 kHz")
]


class EqualizerDialog(QDialog):
    """Діалог налаштування еквалайзера"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sliders = {}
        self._labels = {}
        
        self.setWindowTitle("Еквалайзер")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Ініціалізація UI"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("Еквалайзер")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Інформація
        info_label = QLabel("Налаштуйте рівні для різних частот (від -12 до +12 дБ)")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Сітка з слайдерами
        sliders_widget = QWidget()
        sliders_layout = QHBoxLayout(sliders_widget)
        sliders_layout.setSpacing(10)
        
        for freq, label_text in EQ_BANDS:
            band_widget = self._create_band_widget(freq, label_text)
            sliders_layout.addWidget(band_widget)
        
        layout.addWidget(sliders_widget)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Кнопка скидання
        reset_btn = QPushButton("Скинути")
        reset_btn.clicked.connect(self._reset_all)
        buttons_layout.addWidget(reset_btn)
        
        # Кнопка закриття
        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_band_widget(self, freq: int, label_text: str) -> QWidget:
        """Створює віджет для однієї смуги еквалайзера"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Мітка частоти
        freq_label = QLabel(label_text)
        freq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        freq_label.setMaximumWidth(60)
        layout.addWidget(freq_label)
        
        # Слайдер (вертикальний)
        slider = QSlider(Qt.Orientation.Vertical)
        slider.setMinimum(-12)
        slider.setMaximum(12)
        slider.setValue(0)
        slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        slider.setTickInterval(6)
        slider.setMinimumHeight(200)
        slider.setMaximumWidth(50)
        
        # Підключення до оновлення мітки
        slider.valueChanged.connect(lambda v: self._update_band_label(freq, v))
        
        layout.addWidget(slider, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Мітка значення
        value_label = QLabel("0 dB")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setMaximumWidth(60)
        layout.addWidget(value_label)
        
        # Зберігаємо посилання
        self._sliders[freq] = slider
        self._labels[freq] = value_label
        
        return widget
    
    def _update_band_label(self, freq: int, value: int):
        """Оновлює мітку значення для смуги"""
        if freq in self._labels:
            sign = "+" if value >= 0 else ""
            self._labels[freq].setText(f"{sign}{value} dB")
    
    def _reset_all(self):
        """Скидає всі значення до 0"""
        for slider in self._sliders.values():
            slider.setValue(0)
        self._save_settings()
    
    def get_band_values(self) -> dict:
        """Повертає значення всіх смуг"""
        return {freq: slider.value() for freq, slider in self._sliders.items()}
    
    def set_band_values(self, values: dict):
        """Встановлює значення смуг"""
        for freq, value in values.items():
            if freq in self._sliders:
                self._sliders[freq].setValue(value)
    
    def _save_settings(self):
        """Зберігає налаштування еквалайзера"""
        try:
            # Завантажуємо існуючі налаштування
            settings = {}
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # Додаємо налаштування еквалайзера
            settings['equalizer'] = self.get_band_values()
            
            # Зберігаємо
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            logger.debug("Налаштування еквалайзера збережено")
        except Exception as e:
            logger.error(f"Помилка збереження налаштувань еквалайзера: {e}", exc_info=True)
    
    def _load_settings(self):
        """Завантажує налаштування еквалайзера"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'equalizer' in settings:
                        self.set_band_values(settings['equalizer'])
                        logger.debug("Налаштування еквалайзера завантажено")
        except Exception as e:
            logger.error(f"Помилка завантаження налаштувань еквалайзера: {e}", exc_info=True)
    
    def accept(self):
        """Зберігає налаштування при закритті"""
        self._save_settings()
        super().accept()

