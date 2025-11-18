"""
Утиліти для статистики відтворення
"""
from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime

from .logger import get_logger

logger = get_logger(__name__)

STATS_FILE = Path(__file__).parent.parent.parent / "statistics.json"


class PlayStatistics:
    """Клас для управління статистикою відтворення"""
    
    def __init__(self):
        self._stats: Dict[str, dict] = {}
        self._load_stats()
    
    def _load_stats(self):
        """Завантажує статистику з файлу"""
        try:
            if STATS_FILE.exists():
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._stats = data.get('statistics', {})
                logger.debug(f"Статистика завантажена: {len(self._stats)} треків")
        except Exception as e:
            logger.error(f"Помилка завантаження статистики: {e}", exc_info=True)
            self._stats = {}
    
    def increment_play_count(self, file_path: str):
        """
        Збільшує лічильник відтворень для треку
        
        Args:
            file_path: Шлях до файлу
        """
        try:
            if file_path not in self._stats:
                self._stats[file_path] = {
                    'play_count': 0,
                    'first_played': None,
                    'last_played': None
                }
            
            self._stats[file_path]['play_count'] = self._stats[file_path].get('play_count', 0) + 1
            self._stats[file_path]['last_played'] = datetime.now().isoformat()
            
            if not self._stats[file_path].get('first_played'):
                self._stats[file_path]['first_played'] = datetime.now().isoformat()
            
            self._save_stats()
            logger.debug(f"Лічильник відтворень оновлено для: {file_path}")
        except Exception as e:
            logger.error(f"Помилка оновлення статистики: {e}", exc_info=True)
    
    def get_play_count(self, file_path: str) -> int:
        """
        Повертає кількість відтворень треку
        
        Args:
            file_path: Шлях до файлу
            
        Returns:
            Кількість відтворень
        """
        return self._stats.get(file_path, {}).get('play_count', 0)
    
    def get_stats(self, file_path: str) -> Optional[dict]:
        """
        Повертає повну статистику для треку
        
        Args:
            file_path: Шлях до файлу
            
        Returns:
            Словник зі статистикою або None
        """
        return self._stats.get(file_path)
    
    def get_top_tracks(self, limit: int = 10) -> list:
        """
        Повертає найпопулярніші треки
        
        Args:
            limit: Максимальна кількість треків
            
        Returns:
            Список кортежів (file_path, play_count)
        """
        sorted_tracks = sorted(
            self._stats.items(),
            key=lambda x: x[1].get('play_count', 0),
            reverse=True
        )
        return [(path, stats.get('play_count', 0)) for path, stats in sorted_tracks[:limit]]
    
    def clear_stats(self):
        """Очищає всю статистику"""
        self._stats.clear()
        self._save_stats()
        logger.info("Статистика очищена")
    
    def _save_stats(self):
        """Зберігає статистику у файл"""
        try:
            data = {
                'version': '1.0',
                'statistics': self._stats
            }
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Помилка збереження статистики: {e}", exc_info=True)
    
    def get_all_stats(self) -> Dict[str, dict]:
        """Повертає всю статистику"""
        return self._stats.copy()

