"""
Утиліти для збереження та завантаження стану програвача
"""
from pathlib import Path
import json
from typing import Optional, Dict, Any

from .logger import get_logger

logger = get_logger(__name__)

STATE_FILE = Path(__file__).parent.parent.parent / "state.json"


def save_state(playlist: list, current_index: int, volume: int, position: int = 0, 
               repeat: int = 0, shuffle: bool = False) -> bool:
    """
    Зберігає стан програвача
    
    Args:
        playlist: Список треків
        current_index: Поточний індекс треку
        volume: Гучність
        position: Позиція відтворення (мс)
        repeat: Режим повторення
        shuffle: Режим випадкового відтворення
        
    Returns:
        True якщо успішно збережено
    """
    try:
        state = {
            'playlist': playlist,
            'current_index': current_index,
            'volume': volume,
            'position': position,
            'repeat': repeat,
            'shuffle': shuffle
        }
        
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Стан збережено: {len(playlist)} треків, індекс {current_index}")
        return True
    except Exception as e:
        logger.error(f"Помилка збереження стану: {e}", exc_info=True)
        return False


def load_state() -> Optional[Dict[str, Any]]:
    """
    Завантажує стан програвача
    
    Returns:
        Словник зі станом або None якщо не вдалося завантажити
    """
    try:
        if not STATE_FILE.exists():
            logger.debug("Файл стану не існує")
            return None
        
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Валідуємо дані
        if 'playlist' not in state or not isinstance(state['playlist'], list):
            logger.warning("Невірний формат стану: відсутній плейлист")
            return None
        
        # Фільтруємо тільки існуючі файли
        valid_tracks = [t for t in state['playlist'] if Path(t).exists()]
        if len(valid_tracks) < len(state['playlist']):
            logger.warning(f"Деякі файли зі стану не знайдено: {len(state['playlist']) - len(valid_tracks)}")
        
        state['playlist'] = valid_tracks
        
        # Коригуємо індекс якщо потрібно
        if state.get('current_index', -1) >= len(valid_tracks):
            state['current_index'] = len(valid_tracks) - 1 if valid_tracks else -1
        
        logger.info(f"Стан завантажено: {len(valid_tracks)} треків")
        return state
    except Exception as e:
        logger.error(f"Помилка завантаження стану: {e}", exc_info=True)
        return None


def clear_state() -> bool:
    """
    Очищає збережений стан
    
    Returns:
        True якщо успішно очищено
    """
    try:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
            logger.info("Стан очищено")
        return True
    except Exception as e:
        logger.error(f"Помилка очищення стану: {e}", exc_info=True)
        return False

