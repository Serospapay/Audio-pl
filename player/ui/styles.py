"""
Сучасні стилі для UI
"""
from PyQt6.QtGui import QColor


class ModernStyles:
    """Клас з сучасними стилями для програвача"""
    
    # Кольорова палітра
    COLORS = {
        'background': '#0f0f0f',
        'surface': '#1a1a1a',
        'surface_light': '#252525',
        'primary': '#6366f1',  # Indigo
        'primary_hover': '#818cf8',
        'secondary': '#8b5cf6',  # Purple
        'accent': '#ec4899',  # Pink
        'text_primary': '#ffffff',
        'text_secondary': '#a0a0a0',
        'border': '#2a2a2a',
        'border_light': '#3a3a3a',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
    }
    
    @staticmethod
    def get_main_stylesheet() -> str:
        """Повертає головний stylesheet"""
        colors = ModernStyles.COLORS
        return f"""
            /* Головне вікно */
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['background']}, 
                    stop:1 {colors['surface']});
                color: {colors['text_primary']};
            }}
            
            /* Кнопки */
            QPushButton {{
                background: {colors['surface_light']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px 16px;
                min-width: 100px;
                min-height: 36px;
                color: {colors['text_primary']};
                font-weight: 500;
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background: {colors['primary']};
                border: 1px solid {colors['primary']};
            }}
            
            QPushButton:pressed {{
                background: {colors['secondary']};
                border: 1px solid {colors['secondary']};
            }}
            
            QPushButton:checked {{
                background: {colors['primary']};
                border: 1px solid {colors['primary']};
                color: {colors['text_primary']};
            }}
            
            QPushButton:disabled {{
                background: {colors['surface']};
                color: {colors['text_secondary']};
                border: 1px solid {colors['border']};
            }}
            
            /* Великі кнопки управління */
            QPushButton#controlButton {{
                min-width: 50px;
                min-height: 50px;
                border-radius: 25px;
                font-size: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['primary']}, 
                    stop:1 {colors['secondary']});
                border: none;
            }}
            
            QPushButton#controlButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['primary_hover']}, 
                    stop:1 {colors['primary']});
            }}
            
            /* Плейлист */
            QListWidget {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
                color: {colors['text_primary']};
                padding: 5px;
                outline: none;
            }}
            
            QListWidget::item {{
                padding: 12px;
                border-radius: 8px;
                margin: 2px;
                border: none;
            }}
            
            QListWidget::item:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['surface_light']}, 
                    stop:1 {colors['surface']});
            }}
            
            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['primary']}, 
                    stop:1 {colors['secondary']});
                color: {colors['text_primary']};
            }}
            
            /* Слайдери */
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: {colors['surface_light']};
                border-radius: 3px;
            }}
            
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['primary']}, 
                    stop:1 {colors['secondary']});
                border: 2px solid {colors['text_primary']};
                width: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['primary_hover']}, 
                    stop:1 {colors['primary']});
                width: 24px;
                margin: -9px 0;
            }}
            
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['primary']}, 
                    stop:1 {colors['secondary']});
                border-radius: 3px;
            }}
            
            /* Прогрес бар */
            QSlider#progressSlider::groove:horizontal {{
                height: 8px;
                background: {colors['surface_light']};
            }}
            
            QSlider#progressSlider::handle:horizontal {{
                width: 18px;
                margin: -5px 0;
            }}
            
            /* Фрейми та панелі */
            QFrame {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 16px;
            }}
            
            QFrame#infoPanel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['surface']}, 
                    stop:1 {colors['surface_light']});
                border: 2px solid {colors['border_light']};
                border-radius: 20px;
                padding: 20px;
            }}
            
            /* Лейбли */
            QLabel {{
                color: {colors['text_primary']};
                background: transparent;
            }}
            
            QLabel#titleLabel {{
                font-size: 18px;
                font-weight: 700;
                color: {colors['text_primary']};
            }}
            
            QLabel#artistLabel {{
                font-size: 14px;
                color: {colors['text_secondary']};
            }}
            
            QLabel#timeLabel {{
                font-size: 12px;
                color: {colors['text_secondary']};
                font-weight: 500;
            }}
            
            /* Скроллбари */
            QScrollBar:vertical {{
                background: {colors['surface']};
                width: 12px;
                border: none;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {colors['border_light']};
                min-height: 30px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {colors['primary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            /* Tooltip */
            QToolTip {{
                background: {colors['surface_light']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 5px;
            }}
        """
    
    @staticmethod
    def get_glassmorphism_style() -> str:
        """Повертає стиль glassmorphism для панелей"""
        colors = ModernStyles.COLORS
        return f"""
            background: rgba(26, 26, 26, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
        """

