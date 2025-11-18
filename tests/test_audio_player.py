"""
Тести для модуля audio_player
"""
import pytest
import tempfile
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtMultimedia import QMediaPlayer
from player.audio_player import AudioPlayer


# Ініціалізуємо QApplication для тестів
@pytest.fixture(scope="session")
def qapp():
    """Фікстура для QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestAudioPlayer:
    """Тести для класу AudioPlayer"""
    
    def test_init(self, qapp):
        """Тест ініціалізації програвача"""
        player = AudioPlayer()
        assert player is not None
        assert player.get_volume() == 50
        assert player.get_repeat() is False
        assert player.get_shuffle() is False
        assert player.get_playlist().get_count() == 0
    
    def test_volume_control(self, qapp):
        """Тест контролю гучності"""
        player = AudioPlayer()
        
        # Встановлюємо різні значення гучності
        player.set_volume(0)
        assert player.get_volume() == 0
        
        player.set_volume(50)
        assert player.get_volume() == 50
        
        player.set_volume(100)
        assert player.get_volume() == 100
        
        # Тестуємо обмеження
        player.set_volume(150)
        assert player.get_volume() == 100
        
        player.set_volume(-10)
        assert player.get_volume() == 0
    
    def test_repeat_mode(self, qapp):
        """Тест режиму повторення"""
        player = AudioPlayer()
        
        assert player.get_repeat() is False
        player.set_repeat(True)
        assert player.get_repeat() is True
        player.set_repeat(False)
        assert player.get_repeat() is False
    
    def test_shuffle_mode(self, qapp):
        """Тест режиму випадкового відтворення"""
        player = AudioPlayer()
        
        assert player.get_shuffle() is False
        player.set_shuffle(True)
        assert player.get_shuffle() is True
        player.set_shuffle(False)
        assert player.get_shuffle() is False
    
    def test_playlist_integration(self, qapp):
        """Тест інтеграції з плейлистом"""
        player = AudioPlayer()
        playlist = player.get_playlist()
        
        # Створюємо тимчасові файли
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp.write(b'fake audio data')
                tmp_files.append(tmp.name)
        
        try:
            # Додаємо треки до плейлисту
            added = playlist.add_tracks(tmp_files)
            assert added == 3
            
            # Встановлюємо поточний трек
            playlist.set_current_index(0)
            assert playlist.get_current_index() == 0
            
            # Переходимо до наступного
            track = player.next()
            # Перевіряємо, що індекс змінився
            assert playlist.get_current_index() == 1
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_get_track_info(self, qapp):
        """Тест отримання інформації про трек"""
        player = AudioPlayer()
        
        # Створюємо тимчасовий файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tmp.write(b'fake audio data')
            tmp_path = tmp.name
        
        try:
            info = player.get_track_info(tmp_path)
            assert 'title' in info
            assert 'artist' in info
            assert 'album' in info
            assert 'duration' in info
            assert 'file_path' in info
            assert info['file_path'] == tmp_path
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_get_track_info_nonexistent(self, qapp):
        """Тест отримання інформації про неіснуючий файл"""
        player = AudioPlayer()
        
        info = player.get_track_info("/nonexistent/file.mp3")
        assert 'title' in info
        assert info['title'] == 'file'  # Ім'я файлу без розширення
        assert info['artist'] == 'Невідомий виконавець'

