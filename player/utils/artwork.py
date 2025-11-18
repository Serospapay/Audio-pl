"""
Утиліти для роботи з обкладинками альбомів
"""
from typing import Optional
from PyQt6.QtGui import QPixmap, QImage
from mutagen import File as MutagenFile

from .logger import get_logger

logger = get_logger(__name__)


def extract_artwork(file_path: str) -> Optional[QPixmap]:
    """
    Витягує обкладинку альбому з аудіофайлу
    
    Args:
        file_path: Шлях до аудіофайлу
        
    Returns:
        QPixmap з обкладинкою або None якщо не знайдено
    """
    try:
        audio_file = MutagenFile(file_path)
        if audio_file is None:
            logger.debug(f"Не вдалося відкрити файл для витягування обкладинки: {file_path}")
            return None
        
        # Спробуємо різні теги для обкладинки
        artwork = None
        
        # Для MP3 файлів (ID3)
        if hasattr(audio_file, 'tags'):
            if 'APIC:' in audio_file.tags:
                artwork = audio_file.tags['APIC:'].data
            elif 'APIC' in audio_file.tags:
                # Може бути кілька обкладинок, беремо першу
                apic = audio_file.tags['APIC']
                if isinstance(apic, list):
                    artwork = apic[0].data if apic else None
                else:
                    artwork = apic.data if hasattr(apic, 'data') else None
            elif 'covr' in audio_file.tags:
                # Для M4A/AAC файлів
                covr = audio_file.tags['covr']
                if isinstance(covr, list) and covr:
                    artwork = covr[0] if isinstance(covr[0], bytes) else None
                elif isinstance(covr, bytes):
                    artwork = covr
        
        # Для FLAC, OGG файлів
        if artwork is None:
            if 'metadata_block_picture' in audio_file:
                # FLAC
                picture = audio_file['metadata_block_picture'][0]
                if isinstance(picture, bytes):
                    artwork = picture
            elif 'PICTURE' in audio_file:
                # OGG
                picture = audio_file['PICTURE'][0]
                if isinstance(picture, bytes):
                    artwork = picture
        
        if artwork:
            # Конвертуємо bytes в QPixmap
            image = QImage()
            if image.loadFromData(artwork):
                pixmap = QPixmap.fromImage(image)
                logger.debug(f"Обкладинку знайдено та завантажено: {file_path}")
                return pixmap
            else:
                logger.warning(f"Не вдалося завантажити обкладинку з даних: {file_path}")
        
        logger.debug(f"Обкладинка не знайдена в файлі: {file_path}")
        return None
        
    except Exception as e:
        logger.error(f"Помилка витягування обкладинки з {file_path}: {e}", exc_info=True)
        return None


def create_placeholder_pixmap(size: int = 200) -> QPixmap:
    """
    Створює placeholder обкладинку
    
    Args:
        size: Розмір обкладинки
        
    Returns:
        QPixmap з placeholder
    """
    pixmap = QPixmap(size, size)
    pixmap.fill()  # Заповнюємо прозорим кольором
    
    from PyQt6.QtGui import QPainter, QColor, QFont
    from PyQt6.QtCore import Qt
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Фон з градієнтом
    from PyQt6.QtGui import QLinearGradient
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(60, 60, 80))
    gradient.setColorAt(1, QColor(40, 40, 60))
    painter.fillRect(0, 0, size, size, gradient)
    
    # Іконка музики (простий символ)
    painter.setPen(QColor(150, 150, 150))
    font = QFont()
    font.setPointSize(size // 4)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(0, 0, size, size, Qt.AlignmentFlag.AlignCenter, "♪")
    
    painter.end()
    return pixmap

