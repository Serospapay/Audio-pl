"""
Playlist management module
"""
from typing import List, Optional
from pathlib import Path

from .utils.logger import get_logger

logger = get_logger(__name__)


class Playlist:
    """Клас для управління плейлистом аудіофайлів"""
    
    def __init__(self):
        self._tracks: List[str] = []
        self._current_index: int = -1
    
    def add_track(self, file_path: str) -> bool:
        """
        Додає трек до плейлисту
        
        Args:
            file_path: Шлях до аудіофайлу
            
        Returns:
            True якщо трек успішно додано, False інакше
        """
        try:
            if not file_path:
                logger.warning("Спроба додати трек з порожнім шляхом")
                return False
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.warning(f"Файл не існує: {file_path}")
                return False
            
            if file_path not in self._tracks:
                self._tracks.append(file_path)
                logger.debug(f"Трек додано до плейлисту: {file_path}")
                return True
            else:
                logger.debug(f"Трек вже є в плейлисті: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Помилка додавання треку {file_path}: {e}", exc_info=True)
            return False
    
    def add_tracks(self, file_paths: List[str]) -> int:
        """
        Додає кілька треків до плейлисту
        
        Args:
            file_paths: Список шляхів до аудіофайлів
            
        Returns:
            Кількість успішно доданих треків
        """
        added = 0
        for path in file_paths:
            if self.add_track(path):
                added += 1
        return added
    
    def remove_track(self, index: int) -> bool:
        """
        Видаляє трек з плейлисту за індексом
        
        Args:
            index: Індекс треку для видалення
            
        Returns:
            True якщо трек успішно видалено, False інакше
        """
        if 0 <= index < len(self._tracks):
            removed_track = self._tracks.pop(index)
            
            # Коригуємо поточний індекс якщо потрібно
            if index < self._current_index:
                self._current_index -= 1
            elif index == self._current_index:
                if self._current_index >= len(self._tracks):
                    self._current_index = len(self._tracks) - 1
                if self._current_index < 0:
                    self._current_index = -1
            
            return True
        return False
    
    def clear(self):
        """Очищає плейлист"""
        self._tracks.clear()
        self._current_index = -1
    
    def get_current_track(self) -> Optional[str]:
        """Повертає шлях до поточного треку"""
        if 0 <= self._current_index < len(self._tracks):
            return self._tracks[self._current_index]
        return None
    
    def set_current_index(self, index: int) -> bool:
        """
        Встановлює поточний індекс
        
        Args:
            index: Індекс треку
            
        Returns:
            True якщо індекс встановлено, False інакше
        """
        if 0 <= index < len(self._tracks):
            self._current_index = index
            return True
        return False
    
    def next_track(self) -> Optional[str]:
        """Переходить до наступного треку"""
        if len(self._tracks) == 0:
            return None
        
        if self._current_index < len(self._tracks) - 1:
            self._current_index += 1
        else:
            self._current_index = 0  # Loop to start
        
        return self.get_current_track()
    
    def previous_track(self) -> Optional[str]:
        """Переходить до попереднього треку"""
        if len(self._tracks) == 0:
            return None
        
        if self._current_index > 0:
            self._current_index -= 1
        else:
            self._current_index = len(self._tracks) - 1  # Loop to end
        
        return self.get_current_track()
    
    def get_tracks(self) -> List[str]:
        """Повертає список всіх треків"""
        return self._tracks.copy()
    
    def get_current_index(self) -> int:
        """Повертає поточний індекс"""
        return self._current_index
    
    def get_count(self) -> int:
        """Повертає кількість треків у плейлисті"""
        return len(self._tracks)
    
    def get_track_at(self, index: int) -> Optional[str]:
        """Повертає трек за індексом"""
        if 0 <= index < len(self._tracks):
            return self._tracks[index]
        return None

