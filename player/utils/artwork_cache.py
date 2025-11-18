"""
Кешування обкладинок альбомів
"""
from pathlib import Path
from typing import Optional
import pickle
import hashlib

from PyQt6.QtGui import QPixmap

from .logger import get_logger
from .artwork import extract_artwork, create_placeholder_pixmap

logger = get_logger(__name__)

CACHE_DIR = Path(__file__).parent.parent.parent / "cache"
CACHE_INDEX_FILE = CACHE_DIR / "artwork_cache.pkl"


class ArtworkCache:
    """Клас для кешування обкладинок альбомів"""
    
    def __init__(self, max_size: int = 100):
        """
        Ініціалізує кеш
        
        Args:
            max_size: Максимальна кількість обкладинок в кеші
        """
        self._cache_dir = CACHE_DIR
        self._cache_dir.mkdir(exist_ok=True)
        self._max_size = max_size
        self._index: dict = {}  # {file_path_hash: cache_file_path}
        self._load_index()
    
    def _load_index(self):
        """Завантажує індекс кешу"""
        try:
            if CACHE_INDEX_FILE.exists():
                with open(CACHE_INDEX_FILE, 'rb') as f:
                    self._index = pickle.load(f)
                logger.debug(f"Індекс кешу завантажено: {len(self._index)} записів")
        except Exception as e:
            logger.error(f"Помилка завантаження індексу кешу: {e}", exc_info=True)
            self._index = {}
    
    def _save_index(self):
        """Зберігає індекс кешу"""
        try:
            with open(CACHE_INDEX_FILE, 'wb') as f:
                pickle.dump(self._index, f)
        except Exception as e:
            logger.error(f"Помилка збереження індексу кешу: {e}", exc_info=True)
    
    def _get_file_hash(self, file_path: str) -> str:
        """Генерує хеш для файлу"""
        return hashlib.md5(file_path.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, file_hash: str) -> Path:
        """Повертає шлях до файлу кешу"""
        return self._cache_dir / f"{file_hash}.pkl"
    
    def get_artwork(self, file_path: str) -> Optional[QPixmap]:
        """
        Отримує обкладинку з кешу або витягує з файлу
        
        Args:
            file_path: Шлях до аудіофайлу
            
        Returns:
            QPixmap з обкладинкою або None
        """
        try:
            file_hash = self._get_file_hash(file_path)
            
            # Перевіряємо кеш
            if file_hash in self._index:
                cache_path = self._get_cache_path(file_hash)
                if cache_path.exists():
                    # Перевіряємо чи файл не змінився (за модифікацією)
                    file_mtime = Path(file_path).stat().st_mtime if Path(file_path).exists() else 0
                    cache_mtime = cache_path.stat().st_mtime
                    
                    # Якщо кеш новіший або файл не існує, використовуємо кеш
                    if cache_mtime >= file_mtime:
                        try:
                            with open(cache_path, 'rb') as f:
                                pixmap = pickle.load(f)
                                if isinstance(pixmap, QPixmap):
                                    logger.debug(f"Обкладинка завантажена з кешу: {file_path}")
                                    return pixmap
                        except Exception as e:
                            logger.warning(f"Помилка завантаження з кешу: {e}")
            
            # Якщо немає в кеші, витягуємо з файлу
            pixmap = extract_artwork(file_path)
            
            # Зберігаємо в кеш
            if pixmap and not pixmap.isNull():
                self._save_to_cache(file_hash, pixmap)
            
            return pixmap
        except Exception as e:
            logger.error(f"Помилка отримання обкладинки: {e}", exc_info=True)
            return None
    
    def _save_to_cache(self, file_hash: str, pixmap: QPixmap):
        """Зберігає обкладинку в кеш"""
        try:
            # Перевіряємо розмір кешу
            if len(self._index) >= self._max_size:
                self._cleanup_cache()
            
            cache_path = self._get_cache_path(file_hash)
            with open(cache_path, 'wb') as f:
                pickle.dump(pixmap, f)
            
            self._index[file_hash] = str(cache_path)
            self._save_index()
            logger.debug(f"Обкладинка збережена в кеш: {file_hash}")
        except Exception as e:
            logger.error(f"Помилка збереження в кеш: {e}", exc_info=True)
    
    def _cleanup_cache(self):
        """Очищає старий кеш (видаляє найстаріші файли)"""
        try:
            if not self._index:
                return
            
            # Сортуємо за часом модифікації
            cache_files = []
            for file_hash, cache_path_str in self._index.items():
                cache_path = Path(cache_path_str)
                if cache_path.exists():
                    cache_files.append((cache_path.stat().st_mtime, file_hash, cache_path))
            
            # Сортуємо за часом (найстаріші перші)
            cache_files.sort()
            
            # Видаляємо 20% найстаріших
            to_remove = max(1, len(cache_files) // 5)
            for _, file_hash, cache_path in cache_files[:to_remove]:
                try:
                    cache_path.unlink()
                    del self._index[file_hash]
                except Exception as e:
                    logger.warning(f"Помилка видалення кешу: {e}")
            
            self._save_index()
            logger.debug(f"Очищено {to_remove} записів з кешу")
        except Exception as e:
            logger.error(f"Помилка очищення кешу: {e}", exc_info=True)
    
    def clear_cache(self):
        """Очищає весь кеш"""
        try:
            for cache_path_str in self._index.values():
                cache_path = Path(cache_path_str)
                if cache_path.exists():
                    cache_path.unlink()
            
            self._index.clear()
            self._save_index()
            logger.info("Кеш обкладинок очищено")
        except Exception as e:
            logger.error(f"Помилка очищення кешу: {e}", exc_info=True)
    
    def get_cache_size(self) -> int:
        """Повертає кількість записів в кеші"""
        return len(self._index)

