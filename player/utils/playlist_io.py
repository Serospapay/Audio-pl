"""
Утиліти для збереження та завантаження плейлистів
"""
from pathlib import Path
from typing import List
import urllib.parse

from .logger import get_logger

logger = get_logger(__name__)


def save_m3u_playlist(file_path: str, tracks: List[str]) -> bool:
    """
    Зберігає плейлист у форматі M3U
    
    Args:
        file_path: Шлях до файлу для збереження
        tracks: Список шляхів до треків
        
    Returns:
        True якщо успішно збережено, False інакше
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            # Записуємо заголовок M3U
            f.write("#EXTM3U\n")
            
            for track in tracks:
                track_path = Path(track)
                if track_path.exists():
                    # Записуємо інформацію про трек
                    f.write(f"#EXTINF:-1,{track_path.stem}\n")
                    # Записуємо шлях (абсолютний)
                    abs_path = track_path.absolute()
                    # Для Windows конвертуємо в URL формат
                    url_path = abs_path.as_uri()
                    f.write(f"{url_path}\n")
        
        logger.info(f"Плейлист збережено: {file_path} ({len(tracks)} треків)")
        return True
    except Exception as e:
        logger.error(f"Помилка збереження плейлисту {file_path}: {e}", exc_info=True)
        return False


def load_m3u_playlist(file_path: str) -> List[str]:
    """
    Завантажує плейлист з M3U файлу
    
    Args:
        file_path: Шлях до M3U файлу
        
    Returns:
        Список шляхів до треків
    """
    tracks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Пропускаємо порожні рядки та коментарі (крім #EXTINF)
            if not line or line.startswith('#EXTM3U'):
                i += 1
                continue
            
            # Якщо це #EXTINF, наступний рядок - шлях до файлу
            if line.startswith('#EXTINF'):
                if i + 1 < len(lines):
                    track_line = lines[i + 1].strip()
                    if track_line and not track_line.startswith('#'):
                        # Конвертуємо URL назад у шлях
                        if track_line.startswith('file:///'):
                            # Windows формат
                            track_path = urllib.parse.unquote(track_line[8:])  # Пропускаємо file:///
                            # Виправляємо подвійні слеші
                            track_path = track_path.replace('/', '\\')
                        elif track_line.startswith('file://'):
                            # Unix формат
                            track_path = urllib.parse.unquote(track_line[7:])
                        else:
                            # Відносний або абсолютний шлях
                            track_path = track_line
                        
                        # Перевіряємо чи файл існує
                        if Path(track_path).exists():
                            tracks.append(track_path)
                        else:
                            logger.warning(f"Файл не знайдено: {track_path}")
                        i += 2
                        continue
            i += 1
        
        logger.info(f"Плейлист завантажено: {file_path} ({len(tracks)} треків)")
        return tracks
    except Exception as e:
        logger.error(f"Помилка завантаження плейлисту {file_path}: {e}", exc_info=True)
        return []


def save_json_playlist(file_path: str, tracks: List[str], metadata: dict = None) -> bool:
    """
    Зберігає плейлист у форматі JSON (з додатковими метаданими)
    
    Args:
        file_path: Шлях до файлу для збереження
        tracks: Список шляхів до треків
        metadata: Додаткові метадані (назва плейлисту, дата створення, тощо)
        
    Returns:
        True якщо успішно збережено, False інакше
    """
    try:
        import json
        
        data = {
            'version': '1.0',
            'tracks': tracks,
            'metadata': metadata or {}
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON плейлист збережено: {file_path} ({len(tracks)} треків)")
        return True
    except Exception as e:
        logger.error(f"Помилка збереження JSON плейлисту {file_path}: {e}", exc_info=True)
        return False


def load_json_playlist(file_path: str) -> tuple[List[str], dict]:
    """
    Завантажує плейлист з JSON файлу
    
    Args:
        file_path: Шлях до JSON файлу
        
    Returns:
        Кортеж (список треків, метадані)
    """
    try:
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tracks = data.get('tracks', [])
        metadata = data.get('metadata', {})
        
        # Фільтруємо тільки існуючі файли
        valid_tracks = [t for t in tracks if Path(t).exists()]
        if len(valid_tracks) < len(tracks):
            logger.warning(f"Деякі файли з плейлисту не знайдено: {len(tracks) - len(valid_tracks)}")
        
        logger.info(f"JSON плейлист завантажено: {file_path} ({len(valid_tracks)} треків)")
        return valid_tracks, metadata
    except Exception as e:
        logger.error(f"Помилка завантаження JSON плейлисту {file_path}: {e}", exc_info=True)
        return [], {}

