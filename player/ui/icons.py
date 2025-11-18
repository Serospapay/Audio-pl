"""
SVG іконки для UI (спрощена версія)
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray

from ..utils.logger import get_logger

logger = get_logger(__name__)


class IconProvider:
    """Провайдер іконок для UI"""
    
    # SVG іконки як рядки
    PLAY_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M8 5v14l11-7z"/>
    </svg>
    """
    
    PAUSE_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
    </svg>
    """
    
    STOP_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 6h12v12H6z"/>
    </svg>
    """
    
    PREVIOUS_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
    </svg>
    """
    
    NEXT_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
    </svg>
    """
    
    REPEAT_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
    </svg>
    """
    
    SHUFFLE_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/>
    </svg>
    """
    
    VOLUME_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
    </svg>
    """
    
    ADD_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
    </svg>
    """
    
    DELETE_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
    </svg>
    """
    
    FOLDER_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/>
    </svg>
    """
    
    CLEAR_ICON = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>
    """
    
    @staticmethod
    def svg_to_icon(svg_string: str, size: int = 24, color: str = "#ffffff") -> QIcon:
        """
        Конвертує SVG рядок в QIcon
        
        Args:
            svg_string: SVG рядок
            size: Розмір іконки
            color: Колір іконки
            
        Returns:
            QIcon об'єкт
        """
        try:
            # Замінюємо колір в SVG
            colored_svg = svg_string.replace('currentColor', color).strip()
            
            # Створюємо pixmap
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            # Використовуємо QSvgRenderer
            svg_bytes = QByteArray(colored_svg.encode('utf-8'))
            renderer = QSvgRenderer(svg_bytes)
            
            if renderer.isValid():
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                return QIcon(pixmap)
            else:
                logger.warning(f"Не вдалося створити SVG renderer для іконки")
                return QIcon()  # Порожня іконка
        except Exception as e:
            logger.error(f"Помилка створення іконки: {e}", exc_info=True)
            return QIcon()  # Порожня іконка при помилці
    
    @staticmethod
    def get_icon(icon_name: str, size: int = 24, color: str = "#ffffff") -> QIcon:
        """
        Отримує іконку за назвою
        
        Args:
            icon_name: Назва іконки (play, pause, stop, тощо)
            size: Розмір іконки
            color: Колір іконки
            
        Returns:
            QIcon об'єкт
        """
        try:
            icon_map = {
                'play': IconProvider.PLAY_ICON,
                'pause': IconProvider.PAUSE_ICON,
                'stop': IconProvider.STOP_ICON,
                'previous': IconProvider.PREVIOUS_ICON,
                'next': IconProvider.NEXT_ICON,
                'repeat': IconProvider.REPEAT_ICON,
                'shuffle': IconProvider.SHUFFLE_ICON,
                'volume': IconProvider.VOLUME_ICON,
                'add': IconProvider.ADD_ICON,
                'delete': IconProvider.DELETE_ICON,
                'folder': IconProvider.FOLDER_ICON,
                'clear': IconProvider.CLEAR_ICON,
            }
            
            svg = icon_map.get(icon_name.lower())
            if svg:
                return IconProvider.svg_to_icon(svg, size, color)
            else:
                logger.warning(f"Іконка '{icon_name}' не знайдена")
                return QIcon()  # Порожня іконка якщо не знайдено
        except Exception as e:
            logger.error(f"Помилка отримання іконки '{icon_name}': {e}", exc_info=True)
            return QIcon()

