"""
Утиліти для історії відтворення
"""
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

from .logger import get_logger

logger = get_logger(__name__)

HISTORY_FILE = Path(__file__).parent.parent.parent / "history.json"
MAX_HISTORY_SIZE = 100  # Максимальна кількість записів в історії


class PlayHistory:
    """Клас для управління історією відтворення"""
    
    def __init__(self):
        self._history: List[dict] = []
        self._load_history()
    
    def _load_history(self):
        """Завантажує історію з файлу"""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = data.get('history', [])
                    # Обмежуємо розмір
                    if len(self._history) > MAX_HISTORY_SIZE:
                        self._history = self._history[-MAX_HISTORY_SIZE:]
                logger.debug(f"Історія завантажена: {len(self._history)} записів")
        except Exception as e:
            logger.error(f"Помилка завантаження історії: {e}", exc_info=True)
            self._history = []
    
    def add_track(self, file_path: str, title: str = None, artist: str = None):
        """
        Додає трек до історії
        
        Args:
            file_path: Шлях до файлу
            title: Назва треку
            artist: Виконавець
        """
        try:
            entry = {
                'file_path': file_path,
                'title': title or Path(file_path).stem,
                'artist': artist or 'Невідомий виконавець',
                'timestamp': datetime.now().isoformat()
            }
            
            # Видаляємо якщо вже є в історії (щоб не було дублікатів)
            self._history = [h for h in self._history if h.get('file_path') != file_path]
            
            # Додаємо на початок
            self._history.insert(0, entry)
            
            # Обмежуємо розмір
            if len(self._history) > MAX_HISTORY_SIZE:
                self._history = self._history[:MAX_HISTORY_SIZE]
            
            self._save_history()
            logger.debug(f"Трек додано до історії: {file_path}")
        except Exception as e:
            logger.error(f"Помилка додавання треку до історії: {e}", exc_info=True)
    
    def get_recent(self, limit: int = 20) -> List[dict]:
        """
        Повертає нещодавно відтворені треки
        
        Args:
            limit: Максимальна кількість треків
            
        Returns:
            Список записів історії
        """
        return self._history[:limit]
    
    def clear(self):
        """Очищає історію"""
        self._history.clear()
        self._save_history()
        logger.info("Історія очищена")
    
    def _save_history(self):
        """Зберігає історію у файл"""
        try:
            data = {
                'version': '1.0',
                'history': self._history
            }
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Помилка збереження історії: {e}", exc_info=True)
    
    def get_all(self) -> List[dict]:
        """Повертає всю історію"""
        return self._history.copy()

