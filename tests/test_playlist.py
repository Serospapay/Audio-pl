"""
Тести для модуля playlist
"""
import pytest
import tempfile
import os
from pathlib import Path
from player.playlist import Playlist


class TestPlaylist:
    """Тести для класу Playlist"""
    
    def test_init(self):
        """Тест ініціалізації плейлисту"""
        playlist = Playlist()
        assert playlist.get_count() == 0
        assert playlist.get_current_index() == -1
        assert playlist.get_current_track() is None
    
    def test_add_track(self):
        """Тест додавання треку"""
        playlist = Playlist()
        
        # Створюємо тимчасовий файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tmp_path = tmp.name
        
        try:
            # Додаємо файл
            result = playlist.add_track(tmp_path)
            assert result is True
            assert playlist.get_count() == 1
            assert tmp_path in playlist.get_tracks()
            
            # Спробуємо додати той самий файл знову
            result = playlist.add_track(tmp_path)
            assert result is False  # Не повинен додатися дублікат
            assert playlist.get_count() == 1
        finally:
            # Видаляємо тимчасовий файл
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_add_nonexistent_track(self):
        """Тест додавання неіснуючого файлу"""
        playlist = Playlist()
        result = playlist.add_track("/nonexistent/path/file.mp3")
        assert result is False
        assert playlist.get_count() == 0
    
    def test_add_tracks(self):
        """Тест додавання кількох треків"""
        playlist = Playlist()
        
        # Створюємо тимчасові файли
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_files.append(tmp.name)
        
        try:
            added = playlist.add_tracks(tmp_files)
            assert added == 3
            assert playlist.get_count() == 3
            
            # Додаємо неіснуючі файли
            added = playlist.add_tracks(["/nonexistent1.mp3", "/nonexistent2.mp3"])
            assert added == 0
            assert playlist.get_count() == 3
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_remove_track(self):
        """Тест видалення треку"""
        playlist = Playlist()
        
        # Створюємо тимчасові файли
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_files.append(tmp.name)
        
        try:
            playlist.add_tracks(tmp_files)
            assert playlist.get_count() == 3
            
            # Видаляємо середній трек
            result = playlist.remove_track(1)
            assert result is True
            assert playlist.get_count() == 2
            assert tmp_files[1] not in playlist.get_tracks()
            
            # Видаляємо неіснуючий індекс
            result = playlist.remove_track(10)
            assert result is False
            assert playlist.get_count() == 2
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_remove_track_current_index(self):
        """Тест видалення треку з коректним оновленням поточного індексу"""
        playlist = Playlist()
        
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_files.append(tmp.name)
        
        try:
            playlist.add_tracks(tmp_files)
            playlist.set_current_index(1)
            
            # Видаляємо трек перед поточним
            playlist.remove_track(0)
            assert playlist.get_current_index() == 0
            
            # Видаляємо поточний трек
            playlist.remove_track(0)
            assert playlist.get_current_index() == 0  # Має перейти до наступного
            
            # Видаляємо останній трек
            playlist.remove_track(0)
            assert playlist.get_current_index() == -1
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_clear(self):
        """Тест очищення плейлисту"""
        playlist = Playlist()
        
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_files.append(tmp.name)
        
        try:
            playlist.add_tracks(tmp_files)
            playlist.set_current_index(1)
            
            playlist.clear()
            assert playlist.get_count() == 0
            assert playlist.get_current_index() == -1
            assert playlist.get_current_track() is None
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_set_current_index(self):
        """Тест встановлення поточного індексу"""
        playlist = Playlist()
        
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_files.append(tmp.name)
        
        try:
            playlist.add_tracks(tmp_files)
            
            # Встановлюємо валідний індекс
            result = playlist.set_current_index(1)
            assert result is True
            assert playlist.get_current_index() == 1
            assert playlist.get_current_track() == tmp_files[1]
            
            # Встановлюємо невалідний індекс
            result = playlist.set_current_index(10)
            assert result is False
            assert playlist.get_current_index() == 1
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_next_track(self):
        """Тест переходу до наступного треку"""
        playlist = Playlist()
        
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_files.append(tmp.name)
        
        try:
            playlist.add_tracks(tmp_files)
            playlist.set_current_index(0)
            
            # Переходимо до наступного
            track = playlist.next_track()
            assert track == tmp_files[1]
            assert playlist.get_current_index() == 1
            
            # Переходимо до останнього
            track = playlist.next_track()
            assert track == tmp_files[2]
            assert playlist.get_current_index() == 2
            
            # Переходимо з останнього (має зациклитися)
            track = playlist.next_track()
            assert track == tmp_files[0]
            assert playlist.get_current_index() == 0
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_previous_track(self):
        """Тест переходу до попереднього треку"""
        playlist = Playlist()
        
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_files.append(tmp.name)
        
        try:
            playlist.add_tracks(tmp_files)
            playlist.set_current_index(2)
            
            # Переходимо до попереднього
            track = playlist.previous_track()
            assert track == tmp_files[1]
            assert playlist.get_current_index() == 1
            
            # Переходимо до першого
            track = playlist.previous_track()
            assert track == tmp_files[0]
            assert playlist.get_current_index() == 0
            
            # Переходимо з першого (має зациклитися)
            track = playlist.previous_track()
            assert track == tmp_files[2]
            assert playlist.get_current_index() == 2
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_get_track_at(self):
        """Тест отримання треку за індексом"""
        playlist = Playlist()
        
        tmp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_files.append(tmp.name)
        
        try:
            playlist.add_tracks(tmp_files)
            
            assert playlist.get_track_at(0) == tmp_files[0]
            assert playlist.get_track_at(1) == tmp_files[1]
            assert playlist.get_track_at(2) == tmp_files[2]
            assert playlist.get_track_at(10) is None
            assert playlist.get_track_at(-1) is None
        finally:
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

