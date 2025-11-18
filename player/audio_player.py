"""
Audio player core module
"""
from typing import Optional
from pathlib import Path
import random
from enum import IntEnum
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from mutagen import File as MutagenFile
from mutagen.id3 import ID3NoHeaderError

from .playlist import Playlist
from .utils.logger import get_logger

logger = get_logger(__name__)


class RepeatMode(IntEnum):
    """Режими повторення"""
    OFF = 0  # Без повторення
    ONE = 1  # Повторювати один трек
    ALL = 2  # Повторювати весь плейлист


class AudioPlayer(QObject):
    """Основний клас аудіо програвача"""
    
    # Сигнали для зв'язку з UI
    position_changed = pyqtSignal(int)  # Позиція в мілісекундах
    duration_changed = pyqtSignal(int)  # Тривалість в мілісекундах
    state_changed = pyqtSignal(int)  # Стан програвача
    track_changed = pyqtSignal(str)  # Зміна треку
    error_occurred = pyqtSignal(str)  # Помилка
    
    def __init__(self):
        super().__init__()
        try:
            logger.info("Ініціалізація AudioPlayer")
            self._player = QMediaPlayer()
            self._audio_output = QAudioOutput()
            self._player.setAudioOutput(self._audio_output)
            
            self._playlist = Playlist()
            self._repeat_mode = RepeatMode.OFF
            self._shuffle_mode = False
            self._shuffle_history = []  # Історія відтворених треків для shuffle
            self._volume = 50  # 0-100
            self._history = None  # Історія відтворення (ініціалізується при потребі)
            self._statistics = None  # Статистика відтворення (ініціалізується при потребі)
            self._artwork_cache = None  # Кеш обкладинок (ініціалізується при потребі)
            
            # Підключення сигналів
            self._player.positionChanged.connect(self._on_position_changed)
            self._player.durationChanged.connect(self._on_duration_changed)
            self._player.playbackStateChanged.connect(self._on_state_changed)
            self._player.errorOccurred.connect(self._on_error)
            self._player.mediaStatusChanged.connect(self._on_media_status_changed)
            
            self.set_volume(self._volume)
            logger.info("AudioPlayer успішно ініціалізовано")
        except Exception as e:
            logger.error(f"Помилка ініціалізації AudioPlayer: {e}", exc_info=True)
            raise
    
    def _on_position_changed(self, position: int):
        """Обробник зміни позиції відтворення"""
        self.position_changed.emit(position)
    
    def _on_duration_changed(self, duration: int):
        """Обробник зміни тривалості"""
        self.duration_changed.emit(duration)
    
    def _on_state_changed(self, state: int):
        """Обробник зміни стану програвача"""
        self.state_changed.emit(state)
    
    def _on_error(self, error: int, error_string: str):
        """Обробник помилок"""
        error_msg = f"Помилка відтворення: {error_string}"
        logger.error(f"AudioPlayer помилка [{error}]: {error_string}")
        self.error_occurred.emit(error_msg)
    
    def _on_media_status_changed(self, status: int):
        """Обробник зміни статусу медіа"""
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._handle_track_end()
    
    def _handle_track_end(self):
        """Обробка завершення треку"""
        if self._repeat_mode == RepeatMode.ONE:
            # Повторюємо поточний трек (без додавання до історії)
            current = self._playlist.get_current_track()
            if current:
                self.load_file(current)
                self._player.play()  # Використовуємо _player.play() напряму, щоб не додавати до історії
        elif self._repeat_mode == RepeatMode.ALL:
            # Переходимо до наступного, але якщо це останній - повертаємось до першого
            self.next()
        else:
            # RepeatMode.OFF - просто переходимо до наступного
            self.next()
    
    def load_file(self, file_path: str) -> bool:
        """
        Завантажує аудіофайл
        
        Args:
            file_path: Шлях до аудіофайлу
            
        Returns:
            True якщо файл успішно завантажено, False інакше
        """
        try:
            if not file_path:
                logger.warning("Спроба завантажити файл з порожнім шляхом")
                self.error_occurred.emit("Файл не знайдено")
                return False
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.warning(f"Файл не існує: {file_path}")
                self.error_occurred.emit("Файл не знайдено")
                return False
            
            logger.info(f"Завантаження файлу: {file_path}")
            url = QUrl.fromLocalFile(str(file_path_obj.absolute()))
            self._player.setSource(url)
            logger.debug(f"Файл успішно завантажено: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Помилка завантаження файлу {file_path}: {e}", exc_info=True)
            self.error_occurred.emit(f"Помилка завантаження: {str(e)}")
            return False
    
    def play(self):
        """Починає або продовжує відтворення"""
        if self._player.source().isEmpty():
            # Якщо немає завантаженого файлу, завантажуємо поточний трек з плейлисту
            current = self._playlist.get_current_track()
            if current:
                self.load_file(current)
        
        was_playing = self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        self._player.play()
        
        # Додаємо до історії та статистики тільки якщо це нове відтворення (не було паузи)
        if not was_playing:
            current = self._playlist.get_current_track()
            if current:
                info = self.get_track_info(current)
                self.get_history().add_track(
                    current,
                    info.get('title'),
                    info.get('artist')
                )
                # Оновлюємо статистику
                self.get_statistics().increment_play_count(current)
    
    def pause(self):
        """Призупиняє відтворення"""
        self._player.pause()
    
    def stop(self):
        """Зупиняє відтворення"""
        self._player.stop()
    
    def next(self):
        """Переходить до наступного треку"""
        if self._playlist.get_count() == 0:
            return
        
        if self._shuffle_mode:
            track = self._get_shuffle_next()
        else:
            track = self._playlist.next_track()
        
        if track:
            if self.load_file(track):
                self.play()
                self.track_changed.emit(track)
    
    def _get_shuffle_next(self) -> Optional[str]:
        """Отримує наступний трек у режимі shuffle"""
        tracks = self._playlist.get_tracks()
        if not tracks:
            return None
        
        current_index = self._playlist.get_current_index()
        
        # Якщо всі треки відтворені, очищаємо історію
        if len(self._shuffle_history) >= len(tracks):
            self._shuffle_history.clear()
        
        # Отримуємо доступні треки (ті, що ще не відтворені)
        available_indices = [i for i in range(len(tracks)) if i not in self._shuffle_history]
        
        # Якщо немає доступних, очищаємо історію
        if not available_indices:
            self._shuffle_history.clear()
            available_indices = list(range(len(tracks)))
        
        # Вибираємо випадковий індекс
        next_index = random.choice(available_indices)
        self._shuffle_history.append(next_index)
        
        # Встановлюємо поточний індекс
        self._playlist.set_current_index(next_index)
        return tracks[next_index]
    
    def previous(self):
        """Переходить до попереднього треку"""
        if self._playlist.get_count() == 0:
            return
        
        track = self._playlist.previous_track()
        if track:
            if self.load_file(track):
                self.play()
                self.track_changed.emit(track)
    
    def set_position(self, position: int):
        """
        Встановлює позицію відтворення
        
        Args:
            position: Позиція в мілісекундах
        """
        self._player.setPosition(position)
    
    def get_position(self) -> int:
        """Повертає поточну позицію в мілісекундах"""
        return self._player.position()
    
    def get_duration(self) -> int:
        """Повертає тривалість треку в мілісекундах"""
        return self._player.duration()
    
    def get_state(self) -> int:
        """Повертає поточний стан програвача"""
        return self._player.playbackState()
    
    def set_volume(self, volume: int):
        """
        Встановлює гучність
        
        Args:
            volume: Гучність від 0 до 100
        """
        self._volume = max(0, min(100, volume))
        # QAudioOutput використовує значення від 0.0 до 1.0
        self._audio_output.setVolume(self._volume / 100.0)
    
    def get_volume(self) -> int:
        """Повертає поточну гучність"""
        return self._volume
    
    def set_repeat(self, mode: int):
        """
        Встановлює режим повторення
        
        Args:
            mode: RepeatMode.OFF (0), RepeatMode.ONE (1), або RepeatMode.ALL (2)
        """
        if isinstance(mode, int) and 0 <= mode <= 2:
            self._repeat_mode = RepeatMode(mode)
        else:
            logger.warning(f"Невірний режим повторення: {mode}, встановлюю OFF")
            self._repeat_mode = RepeatMode.OFF
    
    def get_repeat(self) -> int:
        """Повертає поточний режим повторення"""
        return int(self._repeat_mode)
    
    def cycle_repeat_mode(self):
        """Циклічно перемикає режими повторення: OFF -> ONE -> ALL -> OFF"""
        if self._repeat_mode == RepeatMode.OFF:
            self._repeat_mode = RepeatMode.ONE
        elif self._repeat_mode == RepeatMode.ONE:
            self._repeat_mode = RepeatMode.ALL
        else:
            self._repeat_mode = RepeatMode.OFF
        logger.debug(f"Режим повторення змінено на: {self._repeat_mode.name}")
        self.repeat_mode_changed.emit(int(self._repeat_mode))
    
    def get_history(self):
        """Отримує об'єкт історії відтворення"""
        if self._history is None:
            from .utils.history import PlayHistory
            self._history = PlayHistory()
        return self._history
    
    def get_statistics(self):
        """Отримує об'єкт статистики відтворення"""
        if self._statistics is None:
            from .utils.statistics import PlayStatistics
            self._statistics = PlayStatistics()
        return self._statistics
    
    def set_shuffle(self, enabled: bool):
        """Встановлює режим випадкового відтворення"""
        self._shuffle_mode = enabled
        if enabled:
            # Очищаємо історію при увімкненні shuffle
            self._shuffle_history = []
        else:
            # Очищаємо історію при вимкненні shuffle
            self._shuffle_history = []
    
    def get_shuffle(self) -> bool:
        """Повертає стан режиму випадкового відтворення"""
        return self._shuffle_mode
    
    def get_playlist(self) -> Playlist:
        """Повертає об'єкт плейлисту"""
        return self._playlist
    
    def get_track_info(self, file_path: str) -> dict:
        """
        Отримує метадані треку
        
        Args:
            file_path: Шлях до аудіофайлу
            
        Returns:
            Словник з метаданими
        """
        info = {
            'title': Path(file_path).stem,
            'artist': 'Невідомий виконавець',
            'album': 'Невідомий альбом',
            'duration': 0,
            'file_path': file_path,
            'artwork': None
        }
        
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is not None:
                # Отримуємо тривалість
                if hasattr(audio_file, 'info') and hasattr(audio_file.info, 'length'):
                    info['duration'] = int(audio_file.info.length * 1000)  # Конвертуємо в мс
                
                # Отримуємо метадані
                if 'TIT2' in audio_file or 'TITLE' in audio_file:
                    title = audio_file.get('TIT2', audio_file.get('TITLE', ['']))
                    if title:
                        info['title'] = str(title[0])
                
                if 'TPE1' in audio_file or 'ARTIST' in audio_file:
                    artist = audio_file.get('TPE1', audio_file.get('ARTIST', ['']))
                    if artist:
                        info['artist'] = str(artist[0])
                
                if 'TALB' in audio_file or 'ALBUM' in audio_file:
                    album = audio_file.get('TALB', audio_file.get('ALBUM', ['']))
                    if album:
                        info['album'] = str(album[0])
                
                # Отримуємо обкладинку
                # Використовуємо кеш обкладинок
                if self._artwork_cache is None:
                    from .utils.artwork_cache import ArtworkCache
                    self._artwork_cache = ArtworkCache()
                info['artwork'] = self._artwork_cache.get_artwork(file_path)
        except (ID3NoHeaderError, Exception) as e:
            # Якщо не вдалося прочитати метадані, використовуємо значення за замовчуванням
            logger.debug(f"Помилка читання метаданих {file_path}: {e}")
        
        return info

