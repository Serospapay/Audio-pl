"""
Main window UI module
"""
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QFrame, QSizePolicy, QLineEdit, QMenu, QComboBox, QSplitter, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QPoint
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QPixmap, QShortcut, QKeySequence
from PyQt6.QtMultimedia import QMediaPlayer

# Спробуємо імпортувати бібліотеки для покращення UI
try:
    import qdarkstyle
    import qtawesome as qta
    HAS_QTA = True
    HAS_QDARKSTYLE = True
except ImportError:
    HAS_QTA = False
    HAS_QDARKSTYLE = False

from ..audio_player import AudioPlayer


class MainWindow(QMainWindow):
    """Головне вікно програвача"""
    
    def __init__(self):
        super().__init__()
        self._player = AudioPlayer()
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_position)
        self._update_timer.start(100)  # Оновлення кожні 100мс
        
        # Вмикаємо drag & drop
        self.setAcceptDrops(True)
        
        # Таймер для marquee анімації
        self._marquee_timer = QTimer()
        self._marquee_timer.timeout.connect(self._update_marquee)
        self._marquee_position = 0
        self._marquee_direction = 1
        self._original_title = ""
        
        # Режими вікна
        self._compact_mode = False
        self._normal_geometry = None
        
        # Кольори теми
        self._accent_color = "#6366f1"  # Фіолетовий за замовчуванням
        self._accent_hover = "#7c3aed"
        self._accent_pressed = "#5b21b6"
        
        self._init_ui()
        self._connect_signals()
        self._setup_shortcuts()
        self._load_saved_state()
    
    def _init_ui(self):
        """Ініціалізація UI - мінімалістичний дизайн як у Windows Player"""
        self.setWindowTitle("Audio Player")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(700, 500)
        
        # Створюємо меню
        self._create_menu_bar()
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Головний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Застосування темної теми
        self._apply_dark_theme()
        
        # Центральна область - обкладинка та інформація
        center_area = self._create_center_area()
        center_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(center_area, 1)
        
        # Нижня панель - всі контроли в одному рядку
        control_panel = self._create_control_panel()
        control_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(control_panel, 0)
    
    def _apply_dark_theme(self):
        """Застосовує сучасну темну тему"""
        from .styles import ModernStyles
        
        palette = QPalette()
        colors = ModernStyles.COLORS
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 15))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(26, 26, 26))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(37, 37, 37))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(26, 26, 26))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(37, 37, 37))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(236, 72, 153))
        palette.setColor(QPalette.ColorRole.Link, QColor(99, 102, 241))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(99, 102, 241))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Застосовуємо сучасні стилі
        self.setStyleSheet(ModernStyles.get_main_stylesheet() + """
            /* Додаткові стилі для покращення вигляду */
            QLineEdit {
                background: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 10px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 13px;
                selection-background-color: #6366f1;
            }
            
            QLineEdit:focus {
                border: 2px solid #6366f1;
                background: #252525;
            }
            
            QComboBox {
                background: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 10px;
                padding: 8px 12px;
                color: #ffffff;
                min-width: 120px;
            }
            
            QComboBox:hover {
                border: 2px solid #6366f1;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                width: 0;
                height: 0;
            }
            
            QComboBox QAbstractItemView {
                background: #1a1a1a;
                border: 2px solid #6366f1;
                border-radius: 10px;
                selection-background-color: #6366f1;
                color: #ffffff;
            }
            
            QSplitter::handle {
                background: #2a2a2a;
                width: 3px;
            }
            
            QSplitter::handle:hover {
                background: #6366f1;
            }
            
            QSplitter::handle:horizontal {
                width: 3px;
            }
            
            QSplitter::handle:vertical {
                height: 3px;
            }
        """)
    
    def _create_menu_bar(self):
        """Створює меню бар з акуратним стилем"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: #0f0f0f;
                color: #ffffff;
                border-bottom: 1px solid #2a2a2a;
                padding: 4px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #1a1a1a;
            }
            QMenu {
                background: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 30px 8px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #6366f1;
            }
            QMenu::separator {
                height: 1px;
                background: #2a2a2a;
                margin: 4px 8px;
            }
        """)
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        
        add_files_action = file_menu.addAction("Додати файли... (Ctrl+O)")
        add_files_action.triggered.connect(self._add_files)
        
        add_folder_action = file_menu.addAction("Додати папку...")
        add_folder_action.triggered.connect(self._add_folder)
        
        file_menu.addSeparator()
        
        save_playlist_action = file_menu.addAction("Зберегти плейлист...")
        save_playlist_action.triggered.connect(self._save_playlist)
        
        load_playlist_action = file_menu.addAction("Завантажити плейлист...")
        load_playlist_action.triggered.connect(self._load_playlist)
        
        file_menu.addSeparator()
        
        # Останні плейлисти
        recent_menu = file_menu.addMenu("Останні плейлисти")
        self._update_recent_playlists_menu(recent_menu)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Вихід")
        exit_action.triggered.connect(self.close)
        
        # Меню Плейлист
        playlist_menu = menubar.addMenu("Плейлист")
        
        show_playlist_action = playlist_menu.addAction("Показати плейлист (Ctrl+L)")
        show_playlist_action.triggered.connect(self._toggle_playlist)
        
        playlist_menu.addSeparator()
        
        clear_playlist_action = playlist_menu.addAction("Очистити плейлист")
        clear_playlist_action.triggered.connect(self._clear_playlist)
        
        # Меню Інструменти
        tools_menu = menubar.addMenu("Інструменти")
        
        history_action = tools_menu.addAction("Історія відтворення...")
        history_action.triggered.connect(self._show_history)
        
        stats_action = tools_menu.addAction("Статистика...")
        stats_action.triggered.connect(self._show_statistics)
        
        tools_menu.addSeparator()
        
        speed_action = tools_menu.addAction("Швидкість відтворення...")
        speed_action.triggered.connect(self._show_playback_speed)
        
        # Меню Вигляд
        view_menu = menubar.addMenu("Вигляд")
        
        self._compact_mode_action = view_menu.addAction("Компактний режим")
        self._compact_mode_action.setCheckable(True)
        self._compact_mode_action.triggered.connect(self._toggle_compact_mode)
        
        self._always_on_top_action = view_menu.addAction("Завжди зверху")
        self._always_on_top_action.setCheckable(True)
        self._always_on_top_action.triggered.connect(self._toggle_always_on_top)
        
        view_menu.addSeparator()
        
        accent_action = view_menu.addAction("Колір акценту...")
        accent_action.triggered.connect(self._choose_accent_color)
        
        # Меню Довідка
        help_menu = menubar.addMenu("Довідка")
        
        shortcuts_action = help_menu.addAction("Гарячі клавіші...")
        shortcuts_action.triggered.connect(self._show_shortcuts)
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction("Про програму")
        about_action.triggered.connect(self._show_about)
    
    def _show_shortcuts(self):
        """Показує діалог з гарячими клавішами"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Гарячі клавіші")
        dialog.setMinimumSize(450, 400)
        dialog.setStyleSheet("QDialog { background: #0f0f0f; }")
        
        # Escape закриває діалог
        escape_shortcut = QShortcut(QKeySequence("Esc"), dialog)
        escape_shortcut.activated.connect(dialog.accept)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Гарячі клавіші")
        title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        shortcuts_text = """
        <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
        <b>Відтворення:</b><br>
        • Space - Play/Pause<br>
        • Media Keys - Управління з клавіатури<br>
        • Ctrl+S - Stop<br>
        • Ctrl+← - Попередній трек<br>
        • Ctrl+→ - Наступний трек<br>
        • ← - Перемотати назад (10 сек)<br>
        • → - Перемотати вперед (10 сек)<br><br>
        
        <b>Гучність:</b><br>
        • Ctrl+↑ - Збільшити<br>
        • Ctrl+↓ - Зменшити<br><br>
        
        <b>Плейлист:</b><br>
        • Ctrl+O - Додати файли<br>
        • Ctrl+L - Відкрити плейлист<br>
        </div>
        """
        
        text_label = QLabel(shortcuts_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("background: transparent;")
        layout.addWidget(text_label)
        
        layout.addStretch()
        
        close_btn = QPushButton("Закрити")
        close_btn.setFixedSize(80, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background: #7c3aed; }
            QPushButton:pressed { background: #5b21b6; }
        """)
        close_btn.clicked.connect(dialog.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def _show_about(self):
        """Показує діалог Про програму"""
        from PyQt6.QtWidgets import QShortcut
        from PyQt6.QtGui import QKeySequence
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Про програму")
        dialog.setMinimumSize(450, 320)
        dialog.setStyleSheet("QDialog { background: #0f0f0f; }")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Назва програми
        title = QLabel("Audio Player")
        title.setStyleSheet("color: #6366f1; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Версія
        version = QLabel("Версія 1.0")
        version.setStyleSheet("color: #888; font-size: 14px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        layout.addSpacing(10)
        
        # Опис
        description = QLabel("Мінімалістичний аудіоплеєр з сучасним інтерфейсом")
        description.setStyleSheet("color: #ffffff; font-size: 13px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        layout.addSpacing(20)
        
        # Особливості
        features = QLabel(
            "• Підтримка популярних аудіоформатів\n"
            "• Плейлисти та історія відтворення\n"
            "• Статистика прослуховувань\n"
            "• Настроюваний колір акценту\n"
            "• Гарячі клавіші та медіа-клавіші"
        )
        features.setStyleSheet("color: #cccccc; font-size: 12px;")
        layout.addWidget(features)
        
        layout.addStretch()
        
        # Копірайт
        copyright_label = QLabel("© 2024")
        copyright_label.setStyleSheet("color: #666; font-size: 11px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)
        
        # Кнопка закриття
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрити")
        close_btn.setFixedHeight(32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #4f46e5;
            }
            QPushButton:pressed {
                background: #3730a3;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Escape для закриття
        QShortcut(QKeySequence("Esc"), dialog).activated.connect(dialog.accept)
        
        dialog.exec()
    
    def _update_recent_playlists_menu(self, menu):
        """Оновлює меню останніх плейлистів"""
        menu.clear()
        recent = self._get_recent_playlists()
        
        if not recent:
            no_recent = menu.addAction("Немає останніх плейлистів")
            no_recent.setEnabled(False)
            return
        
        for playlist_path in recent:
            action = menu.addAction(Path(playlist_path).name)
            action.triggered.connect(lambda checked, path=playlist_path: self._load_recent_playlist(path))
    
    def _get_recent_playlists(self):
        """Отримує список останніх плейлистів"""
        try:
            from player.utils.state_manager import load_state
            state = load_state()
            return state.get('recent_playlists', [])[:5]  # Максимум 5
        except:
            return []
    
    def _save_recent_playlist(self, playlist_path):
        """Зберігає плейлист в список останніх"""
        try:
            from player.utils.state_manager import load_state, save_state
            state = load_state()
            recent = state.get('recent_playlists', [])
            
            # Видаляємо якщо вже є
            if playlist_path in recent:
                recent.remove(playlist_path)
            
            # Додаємо на початок
            recent.insert(0, playlist_path)
            
            # Зберігаємо максимум 5
            recent = recent[:5]
            
            state['recent_playlists'] = recent
            save_state(**state)
        except Exception as e:
            print(f"Error saving recent playlist: {e}")
    
    def _load_recent_playlist(self, playlist_path):
        """Завантажує плейлист з останніх"""
        if not Path(playlist_path).exists():
            QMessageBox.warning(self, "Помилка", f"Файл не знайдено:\n{playlist_path}")
            return
        
        from player.utils.playlist_io import load_m3u_playlist, load_json_playlist
        
        if playlist_path.endswith('.json'):
            tracks, metadata = load_json_playlist(playlist_path)
        else:
            tracks = load_m3u_playlist(playlist_path)
        
        if tracks:
            # Замінюємо поточний плейлист
            self._player.get_playlist().clear()
            added = self._player.get_playlist().add_tracks(tracks)
            self._update_playlist_display()
            QMessageBox.information(self, "Успіх", f"Завантажено {added} треків!")
    
    def _show_statistics(self):
        """Показує розширену статистику з топ-10 та загальним часом"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Статистика")
        dialog.setMinimumSize(650, 550)
        dialog.setStyleSheet("QDialog { background: #0f0f0f; }")
        
        # Escape закриває діалог
        escape_shortcut = QShortcut(QKeySequence("Esc"), dialog)
        escape_shortcut.activated.connect(dialog.accept)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("Статистика відтворення")
        title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Отримуємо дані
        playlist = self._player.get_playlist()
        history = self._player.get_history()
        history_data = history.get_history()
        
        # Рахуємо загальний час та частоту
        total_time_ms = 0
        track_counts = {}
        
        for entry in history_data:
            file_path = entry.get('file_path')
            if file_path and Path(file_path).exists():
                # Отримуємо тривалість треку
                info = self._player.get_track_info(file_path)
                duration = info.get('duration', 0)
                total_time_ms += duration
                
                # Рахуємо кількість відтворень
                track_key = f"{info.get('title', 'Unknown')} - {info.get('artist', 'Unknown')}"
                track_counts[track_key] = track_counts.get(track_key, 0) + 1
        
        # Топ-10 треків
        top_tracks = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Форматуємо загальний час
        total_hours = total_time_ms // (1000 * 3600)
        total_minutes = (total_time_ms % (1000 * 3600)) // (1000 * 60)
        
        # Основна статистика
        stats_text = f"""
        <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
        <b>📊 Загальна статистика:</b><br>
        • Треків у плейлисті: <span style='color: #6366f1;'>{len(playlist.get_tracks())}</span><br>
        • Всього відтворено: <span style='color: #6366f1;'>{len(history_data)}</span><br>
        • Загальний час: <span style='color: #6366f1;'>{total_hours}г {total_minutes}хв</span><br>
        • Унікальних треків: <span style='color: #6366f1;'>{len(track_counts)}</span><br><br>
        
        <b>🎵 Режими відтворення:</b><br>
        • Повтор: <span style='color: {"#10b981" if self._player.get_repeat() else "#ef4444"};'>{'✓ Увімкнено' if self._player.get_repeat() else '✗ Вимкнено'}</span><br>
        • Shuffle: <span style='color: {"#10b981" if self._player.get_shuffle() else "#ef4444"};'>{'✓ Увімкнено' if self._player.get_shuffle() else '✗ Вимкнено'}</span><br>
        • Гучність: <span style='color: #6366f1;'>{self._player.get_volume()}%</span><br>
        </div>
        """
        
        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        stats_label.setStyleSheet("background: transparent;")
        layout.addWidget(stats_label)
        
        # Топ-10 треків
        if top_tracks:
            top_title = QLabel("🏆 Топ-10 найчастіше відтворюваних:")
            top_title.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; margin-top: 10px;")
            layout.addWidget(top_title)
            
            top_list = QListWidget()
            top_list.setFixedHeight(180)
            top_list.setStyleSheet("""
                QListWidget {
                    background: #1a1a1a;
                    border: 1px solid #2a2a2a;
                    border-radius: 6px;
                    padding: 5px;
                    color: #ffffff;
                    font-size: 12px;
                }
                QListWidget::item {
                    padding: 5px;
                    border-radius: 3px;
                }
                QListWidget::item:hover {
                    background: #2a2a2a;
                }
            """)
            
            for i, (track, count) in enumerate(top_tracks, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                item_text = f"{medal} {track} - {count} разів"
                top_list.addItem(item_text)
            
            layout.addWidget(top_list)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("Експорт")
        export_btn.setFixedSize(80, 32)
        export_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #6366f1;
                border-radius: 4px;
                color: #6366f1;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background: #6366f1;
                color: #ffffff;
            }
        """)
        export_btn.clicked.connect(lambda: self._export_statistics(total_hours, total_minutes, len(history_data), top_tracks))
        buttons_layout.addWidget(export_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрити")
        close_btn.setFixedSize(80, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            QPushButton:hover { background: #7c3aed; }
            QPushButton:pressed { background: #5b21b6; }
        """)
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec()
    
    def _export_statistics(self, hours, minutes, total_plays, top_tracks):
        """Експортує статистику в текстовий файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Експорт статистики",
            f"statistics_{Path.cwd()}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 50 + "\n")
                    f.write("СТАТИСТИКА AUDIO PLAYER\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Всього відтворено: {total_plays}\n")
                    f.write(f"Загальний час: {hours}г {minutes}хв\n\n")
                    f.write("ТОП-10 ТРЕКІВ:\n")
                    f.write("-" * 50 + "\n")
                    for i, (track, count) in enumerate(top_tracks, 1):
                        f.write(f"{i}. {track} - {count} разів\n")
                    f.write("\n" + "=" * 50 + "\n")
                
                QMessageBox.information(self, "Успіх", f"Статистика експортована в:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Помилка", f"Не вдалося експортувати статистику:\n{str(e)}")
    
    def _toggle_compact_mode(self):
        """Перемикає компактний режим"""
        self._compact_mode = not self._compact_mode
        
        if self._compact_mode:
            # Зберігаємо поточну геометрію
            self._normal_geometry = self.geometry()
            
            # Компактний режим - тільки кнопки управління
            self.setFixedSize(400, 120)
            
            # Приховуємо центральну область
            center_widget = self.centralWidget()
            if center_widget:
                for child in center_widget.findChildren(QWidget):
                    if child.objectName() != "controlPanel":
                        child.hide()
            
            self.setWindowTitle("♫ Audio Player (Compact)")
        else:
            # Відновлюємо нормальний режим
            self.setMinimumSize(700, 500)
            self.setMaximumSize(16777215, 16777215)  # QWIDGETSIZE_MAX
            
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            else:
                self.resize(900, 600)
            
            # Показуємо всі віджети
            center_widget = self.centralWidget()
            if center_widget:
                for child in center_widget.findChildren(QWidget):
                    child.show()
            
            self.setWindowTitle("Audio Player")
    
    def _toggle_always_on_top(self):
        """Перемикає режим 'завжди зверху'"""
        if self._always_on_top_action.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()  # Потрібно для застосування зміни flags
    
    def _choose_accent_color(self):
        """Діалог вибору кольору акценту"""
        from PyQt6.QtWidgets import QColorDialog, QShortcut
        from PyQt6.QtGui import QColor, QKeySequence
        
        # Попередньо встановлені кольори
        presets = [
            ("#6366f1", "Фіолетовий (за замовчуванням)"),
            ("#3b82f6", "Синій"),
            ("#10b981", "Зелений"),
            ("#f59e0b", "Помаранчевий"),
            ("#ef4444", "Червоний"),
            ("#ec4899", "Рожевий"),
            ("#8b5cf6", "Індиго"),
            ("#06b6d4", "Бірюзовий"),
        ]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Виберіть колір акценту")
        dialog.setMinimumSize(450, 320)
        dialog.setStyleSheet("QDialog { background: #0f0f0f; }")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("Виберіть колір акценту")
        title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Попередньо встановлені кольори
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(10)
        
        for color, name in presets:
            btn = QPushButton()
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    border: 2px solid {"#ffffff" if color == self._accent_color else "#2a2a2a"};
                    border-radius: 25px;
                }}
                QPushButton:hover {{
                    border: 2px solid #ffffff;
                    transform: scale(1.1);
                }}
            """)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, c=color: self._apply_accent_color(c, dialog))
            presets_layout.addWidget(btn)
        
        layout.addLayout(presets_layout)
        
        # Кнопка вибору власного кольору
        custom_btn = QPushButton("Вибрати власний колір...")
        custom_btn.setFixedHeight(36)
        custom_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                padding: 8px;
            }
            QPushButton:hover {
                background: #2a2a2a;
                border: 1px solid #6366f1;
            }
        """)
        custom_btn.clicked.connect(lambda: self._choose_custom_color(dialog))
        layout.addWidget(custom_btn)
        
        layout.addStretch()
        
        # Поточний колір
        current_label = QLabel(f"Поточний колір: {self._accent_color}")
        current_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(current_label)
        
        # Escape для закриття
        QShortcut(QKeySequence("Esc"), dialog).activated.connect(dialog.accept)
        
        dialog.exec()
    
    def _choose_custom_color(self, parent_dialog):
        """Відкриває стандартний діалог вибору кольору"""
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        color = QColorDialog.getColor(QColor(self._accent_color), self, "Виберіть колір")
        if color.isValid():
            hex_color = color.name()
            self._apply_accent_color(hex_color, parent_dialog)
    
    def _apply_accent_color(self, color, dialog=None):
        """Застосовує новий колір акценту"""
        self._accent_color = color
        
        # Розраховуємо hover та pressed кольори (трохи світліше/темніше)
        from PyQt6.QtGui import QColor
        base = QColor(color)
        
        # Hover - світліший
        hover = base.lighter(120)
        self._accent_hover = hover.name()
        
        # Pressed - темніший
        pressed = base.darker(120)
        self._accent_pressed = pressed.name()
        
        # Оновлюємо стилі
        self._update_button_styles()
        
        if dialog:
            dialog.accept()
        
        QMessageBox.information(self, "Успіх", f"Колір акценту змінено на {color}\n\nПерезапустіть програму для повного застосування змін.")
    
    def _update_button_styles(self):
        """Оновлює стилі кнопок з новим кольором"""
        # Оновлюємо Play/Pause кнопку
        if hasattr(self, '_play_pause_btn'):
            self._play_pause_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self._accent_color};
                    border: none;
                    border-radius: 20px;
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 0px;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background: {self._accent_hover};
                    transform: scale(1.1);
                }}
                QPushButton:pressed {{
                    background: {self._accent_pressed};
                    transform: scale(0.95);
                }}
            """)
    
    def _on_artwork_click(self, event):
        """Обробник кліку на обкладинку"""
        from PyQt6.QtCore import Qt
        if event.button() == Qt.MouseButton.LeftButton:
            self._add_files()
    
    def _show_artwork_context_menu(self, position):
        """Показує контекстне меню для обкладинки"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #6366f1;
            }
        """)
        
        save_action = menu.addAction("Зберегти обкладинку...")
        save_action.triggered.connect(self._save_artwork)
        
        copy_action = menu.addAction("Копіювати обкладинку")
        copy_action.triggered.connect(self._copy_artwork)
        
        menu.addSeparator()
        
        change_action = menu.addAction("Змінити обкладинку...")
        change_action.triggered.connect(self._change_artwork)
        
        menu.exec(self._artwork_label.mapToGlobal(position))
    
    def _save_artwork(self):
        """Зберігає обкладинку в файл"""
        pixmap = self._artwork_label.pixmap()
        if not pixmap or pixmap.isNull():
            QMessageBox.warning(self, "Помилка", "Немає обкладинки для збереження!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти обкладинку",
            "artwork.png",
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*.*)"
        )
        
        if file_path:
            if pixmap.save(file_path):
                QMessageBox.information(self, "Успіх", f"Обкладинку збережено в:\n{file_path}")
            else:
                QMessageBox.warning(self, "Помилка", "Не вдалося зберегти обкладинку!")
    
    def _copy_artwork(self):
        """Копіює обкладинку в буфер обміну"""
        from PyQt6.QtWidgets import QApplication
        pixmap = self._artwork_label.pixmap()
        if not pixmap or pixmap.isNull():
            QMessageBox.warning(self, "Помилка", "Немає обкладинки для копіювання!")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)
        QMessageBox.information(self, "Успіх", "Обкладинку скопійовано в буфер обміну!")
    
    def _change_artwork(self):
        """Змінює обкладинку треку"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Вибрати обкладинку",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        
        if file_path:
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
                self._artwork_label.setPixmap(scaled)
                QMessageBox.information(self, "Успіх", "Обкладинку змінено!")
            else:
                QMessageBox.warning(self, "Помилка", "Не вдалося завантажити зображення!")
    
    def _show_playback_speed(self):
        """Показує діалог налаштування швидкості відтворення"""
        from PyQt6.QtWidgets import QShortcut
        from PyQt6.QtGui import QKeySequence
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Швидкість відтворення")
        dialog.setMinimumSize(480, 280)
        dialog.setStyleSheet("QDialog { background: #0f0f0f; }")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("Налаштування швидкості відтворення")
        title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Слайдер швидкості
        speed_layout = QHBoxLayout()
        
        speed_label = QLabel("Швидкість:")
        speed_label.setStyleSheet("color: #ffffff; font-size: 13px;")
        speed_layout.addWidget(speed_label)
        
        speed_slider = QSlider(Qt.Orientation.Horizontal)
        speed_slider.setMinimum(25)  # 0.25x
        speed_slider.setMaximum(200)  # 2.0x
        speed_slider.setValue(100)  # 1.0x за замовчуванням
        speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: #2a2a2a;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #6366f1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #6366f1;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)
        speed_layout.addWidget(speed_slider, 1)
        
        speed_value = QLabel("1.0x")
        speed_value.setStyleSheet("color: #6366f1; font-size: 14px; font-weight: bold;")
        speed_value.setFixedWidth(50)
        speed_layout.addWidget(speed_value)
        
        layout.addLayout(speed_layout)
        
        # Оновлення значення при зміні слайдера
        def update_speed(value):
            speed = value / 100.0
            speed_value.setText(f"{speed:.2f}x")
            # Тут можна додати код для зміни швидкості відтворення
            # self._player.set_playback_rate(speed)
        
        speed_slider.valueChanged.connect(update_speed)
        
        # Пресети
        presets_label = QLabel("Пресети:")
        presets_label.setStyleSheet("color: #888; font-size: 12px; margin-top: 10px;")
        layout.addWidget(presets_label)
        
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(8)
        
        for speed, label in [(25, "0.25x"), (50, "0.5x"), (75, "0.75x"), (100, "1.0x"), (125, "1.25x"), (150, "1.5x"), (200, "2.0x")]:
            btn = QPushButton(label)
            btn.setFixedSize(55, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a1a;
                    border: 1px solid #2a2a2a;
                    border-radius: 4px;
                    color: #ffffff;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #6366f1;
                    border: 1px solid #6366f1;
                }
            """)
            btn.clicked.connect(lambda checked, s=speed: speed_slider.setValue(s))
            presets_layout.addWidget(btn)
        
        layout.addLayout(presets_layout)
        
        layout.addStretch()
        
        # Примітка
        note = QLabel("⚠️ Функція зміни швидкості в розробці")
        note.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(note)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрити")
        close_btn.setFixedHeight(32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #4f46e5;
            }
            QPushButton:pressed {
                background: #3730a3;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Escape для закриття
        QShortcut(QKeySequence("Esc"), dialog).activated.connect(dialog.accept)
        
        dialog.exec()
    
    def _create_center_area(self) -> QWidget:
        """Створює центральну область з обкладинкою та інформацією"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Велика обкладинка альбому по центру - клікабельна для відкриття файлів
        self._artwork_label = QLabel()
        self._artwork_label.setMinimumSize(300, 300)
        self._artwork_label.setMaximumSize(400, 400)
        self._artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._artwork_label.setScaledContents(True)
        self._artwork_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._artwork_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2a, stop:1 #0a0a1a);
                border: 3px solid #2a2a3a;
                border-radius: 15px;
            }
            QLabel:hover {
                border: 3px solid #6366f1;
                cursor: pointer;
            }
        """)
        # Робимо клікабельною з контекстним меню
        self._artwork_label.mousePressEvent = self._on_artwork_click
        self._artwork_label.setToolTip("Клікніть, щоб додати аудіофайли\nПКМ - контекстне меню")
        self._artwork_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._artwork_label.customContextMenuRequested.connect(self._show_artwork_context_menu)
        # Встановлюємо placeholder
        from player.utils.artwork import create_placeholder_pixmap
        placeholder = create_placeholder_pixmap(350)
        self._artwork_label.setPixmap(placeholder)
        layout.addWidget(self._artwork_label, 1, Qt.AlignmentFlag.AlignCenter)
        
        # Інформація про трек
        info_container = QWidget()
        info_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)
        
        # Назва треку - також клікабельна
        self._track_title_label = QLabel("Клікніть на обкладинку, щоб додати треки")
        self._track_title_label.setObjectName("titleLabel")
        self._track_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(QFont.Weight.Bold)
        self._track_title_label.setFont(font)
        self._track_title_label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        self._track_title_label.setWordWrap(True)
        self._track_title_label.mousePressEvent = lambda e: self._add_files()
        self._track_title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        info_layout.addWidget(self._track_title_label, 0)
        
        # Виконавець та альбом
        artist_album_layout = QHBoxLayout()
        artist_album_layout.setContentsMargins(0, 0, 0, 0)
        artist_album_layout.setSpacing(10)
        artist_album_layout.addStretch()
        
        self._track_artist_label = QLabel("")
        self._track_artist_label.setObjectName("artistLabel")
        self._track_artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font2 = QFont()
        font2.setPointSize(13)
        font2.setWeight(QFont.Weight.Medium)
        self._track_artist_label.setFont(font2)
        self._track_artist_label.setStyleSheet("color: #a0a0a0; background: transparent; border: none;")
        artist_album_layout.addWidget(self._track_artist_label, 0)
        
        # Роздільник
        separator = QLabel("•")
        separator.setStyleSheet("color: #666; background: transparent; font-size: 12px;")
        separator.setFixedWidth(10)
        artist_album_layout.addWidget(separator, 0)
        
        self._album_label = QLabel("")
        self._album_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font3 = QFont()
        font3.setPointSize(13)
        self._album_label.setFont(font3)
        self._album_label.setStyleSheet("color: #808080; background: transparent; border: none;")
        artist_album_layout.addWidget(self._album_label, 0)
        
        artist_album_layout.addStretch()
        info_layout.addLayout(artist_album_layout, 0)
        
        layout.addWidget(info_container, 0)
        
        return widget
    
    def _create_compact_top_panel(self) -> QFrame:
        """Створює компактну верхню панель з інформацією та контролами"""
        frame = QFrame()
        frame.setObjectName("infoPanel")
        frame.setMinimumHeight(160)
        frame.setMaximumHeight(180)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Компактна обкладинка альбому
        self._artwork_label = QLabel()
        self._artwork_label.setFixedSize(120, 120)
        self._artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._artwork_label.setScaledContents(True)
        self._artwork_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._artwork_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a3a, stop:1 #1a1a2a);
                border: 2px solid #6366f1;
                border-radius: 10px;
            }
        """)
        # Встановлюємо placeholder
        from player.utils.artwork import create_placeholder_pixmap
        placeholder = create_placeholder_pixmap(120)
        self._artwork_label.setPixmap(placeholder)
        layout.addWidget(self._artwork_label, 0)
        
        # Компактна інформація про трек
        info_container = QWidget()
        info_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 8, 0, 8)
        info_layout.setSpacing(10)
        
        # Назва треку
        self._track_title_label = QLabel("Оберіть трек для відтворення")
        self._track_title_label.setObjectName("titleLabel")
        self._track_title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(QFont.Weight.Bold)
        self._track_title_label.setFont(font)
        self._track_title_label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        self._track_title_label.setWordWrap(True)
        self._track_title_label.setMinimumHeight(28)
        self._track_title_label.setMaximumHeight(60)
        self._track_title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout.addWidget(self._track_title_label, 0)
        
        # Виконавець та альбом в один ряд
        artist_album_layout = QHBoxLayout()
        artist_album_layout.setContentsMargins(0, 0, 0, 0)
        artist_album_layout.setSpacing(10)
        
        self._track_artist_label = QLabel("")
        self._track_artist_label.setObjectName("artistLabel")
        self._track_artist_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font2 = QFont()
        font2.setPointSize(11)
        font2.setWeight(QFont.Weight.Medium)
        self._track_artist_label.setFont(font2)
        self._track_artist_label.setStyleSheet("color: #a0a0a0; background: transparent; border: none;")
        self._track_artist_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        artist_album_layout.addWidget(self._track_artist_label, 0)
        
        # Роздільник
        separator = QLabel("•")
        separator.setStyleSheet("color: #666; background: transparent; font-size: 10px;")
        separator.setFixedWidth(8)
        separator.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        artist_album_layout.addWidget(separator, 0)
        
        self._album_label = QLabel("")
        self._album_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font3 = QFont()
        font3.setPointSize(11)
        self._album_label.setFont(font3)
        self._album_label.setStyleSheet("color: #808080; background: transparent; border: none;")
        self._album_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        artist_album_layout.addWidget(self._album_label, 0)
        
        artist_album_layout.addStretch()
        info_layout.addLayout(artist_album_layout, 0)
        
        info_layout.addStretch()
        layout.addWidget(info_container, 1)
        
        # Компактна панель контролів справа
        controls_right = QWidget()
        controls_right.setMinimumWidth(220)
        controls_right.setMaximumWidth(240)
        controls_right.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        controls_layout = QVBoxLayout(controls_right)
        controls_layout.setContentsMargins(12, 8, 12, 8)
        controls_layout.setSpacing(12)
        
        # Гучність компактно
        volume_label = QLabel("Гучність")
        volume_label.setStyleSheet("color: #a0a0a0; font-size: 11px;")
        volume_label.setFixedHeight(20)
        volume_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        controls_layout.addWidget(volume_label, 0)
        
        volume_layout = QHBoxLayout()
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(10)
        
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setMinimum(0)
        self._volume_slider.setMaximum(100)
        self._volume_slider.setValue(50)
        self._volume_slider.setFixedHeight(22)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        self._volume_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        volume_layout.addWidget(self._volume_slider, 1)
        
        self._volume_label = QLabel("50%")
        self._volume_label.setFixedWidth(42)
        self._volume_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._volume_label.setStyleSheet("color: #a0a0a0; font-size: 10px;")
        self._volume_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        volume_layout.addWidget(self._volume_label, 0)
        
        controls_layout.addLayout(volume_layout, 0)
        
        # Режими в один ряд - з правильними відступами
        modes_container = QWidget()
        modes_container.setFixedHeight(36)
        modes_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        modes_layout = QHBoxLayout(modes_container)
        modes_layout.setContentsMargins(0, 4, 0, 4)
        modes_layout.setSpacing(10)
        
        # Repeat button з іконкою
        if HAS_QTA:
            repeat_icon = qta.icon('fa5s.redo', color='#ffffff')
            self._repeat_btn = QPushButton(repeat_icon, "")
        else:
            self._repeat_btn = QPushButton("R")
        self._repeat_btn.setFixedSize(28, 28)
        self._repeat_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._repeat_btn.setToolTip("Repeat: Off")
        self._repeat_btn.setCheckable(True)
        self._repeat_btn.clicked.connect(self._on_repeat_clicked)
        modes_layout.addWidget(self._repeat_btn, 0)
        
        # Shuffle button з іконкою
        if HAS_QTA:
            shuffle_icon = qta.icon('fa5s.random', color='#ffffff')
            self._shuffle_btn = QPushButton(shuffle_icon, "")
        else:
            self._shuffle_btn = QPushButton("S")
        self._shuffle_btn.setFixedSize(28, 28)
        self._shuffle_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._shuffle_btn.setToolTip("Shuffle")
        self._shuffle_btn.setCheckable(True)
        self._shuffle_btn.clicked.connect(self._on_shuffle_toggled)
        modes_layout.addWidget(self._shuffle_btn, 0)
        
        modes_layout.addStretch()
        controls_layout.addWidget(modes_container, 0)
        
        # Додаткові кнопки в один ряд - з правильними відступами
        extras_container = QWidget()
        extras_container.setFixedHeight(36)
        extras_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        extras_layout = QHBoxLayout(extras_container)
        extras_layout.setContentsMargins(0, 4, 0, 4)
        extras_layout.setSpacing(10)
        
        # Settings button з іконкою
        if HAS_QTA:
            settings_icon = qta.icon('fa5s.cog', color='#ffffff')
            self._settings_btn = QPushButton(settings_icon, "")
        else:
            self._settings_btn = QPushButton("⚙")
        self._settings_btn.setFixedSize(28, 28)
        self._settings_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._settings_btn.setToolTip("Налаштування")
        self._settings_btn.clicked.connect(self._show_settings)
        extras_layout.addWidget(self._settings_btn, 0)
        
        # History button з іконкою
        if HAS_QTA:
            history_icon = qta.icon('fa5s.history', color='#ffffff')
            self._history_btn = QPushButton(history_icon, "")
        else:
            self._history_btn = QPushButton("H")
        self._history_btn.setFixedSize(28, 28)
        self._history_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._history_btn.setToolTip("Історія")
        self._history_btn.clicked.connect(self._show_history)
        extras_layout.addWidget(self._history_btn, 0)
        
        # Equalizer button з іконкою
        if HAS_QTA:
            eq_icon = qta.icon('fa5s.sliders-h', color='#ffffff')
            self._equalizer_btn = QPushButton(eq_icon, "")
        else:
            self._equalizer_btn = QPushButton("E")
        self._equalizer_btn.setFixedSize(28, 28)
        self._equalizer_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._equalizer_btn.setToolTip("Еквалайзер")
        self._equalizer_btn.clicked.connect(self._show_equalizer)
        extras_layout.addWidget(self._equalizer_btn, 0)
        
        extras_layout.addStretch()
        controls_layout.addWidget(extras_container, 0)
        
        controls_layout.addStretch()
        layout.addWidget(controls_right, 0)
        
        return frame
    
    def _create_playlist_widget(self) -> QWidget:
        """Створює компактний віджет плейлисту"""
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Компактний заголовок з пошуком в один ряд
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        title = QLabel("Плейлист")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #ffffff; background: transparent;")
        title.setFixedHeight(26)
        title.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        header_layout.addWidget(title, 0)
        
        # Компактний пошук
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Пошук...")
        self._search_input.textChanged.connect(self._filter_playlist)
        self._search_input.setFixedHeight(30)
        self._search_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._search_input.setStyleSheet("""
            QLineEdit {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #6366f1;
                background: #252525;
            }
        """)
        header_layout.addWidget(self._search_input)
        
        layout.addLayout(header_layout, 0)
        
        # Список треків
        self._playlist_widget = QListWidget()
        self._playlist_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._playlist_widget.itemDoubleClicked.connect(self._on_playlist_item_double_clicked)
        self._playlist_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._playlist_widget.customContextMenuRequested.connect(self._show_playlist_context_menu)
        # Увімкнення drag & drop
        self._playlist_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._playlist_widget.model().rowsInserted.connect(self._on_playlist_reordered)
        layout.addWidget(self._playlist_widget, 1)
        
        # Компактна панель кнопок - з правильними відступами
        buttons_container = QWidget()
        buttons_container.setFixedHeight(36)
        buttons_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 4, 0, 4)
        buttons_layout.setSpacing(8)
        
        # Кнопки дій з іконками - фіксовані розміри
        if HAS_QTA:
            add_icon = qta.icon('fa5s.plus', color='#ffffff')
            self._add_files_btn = QPushButton(add_icon, "")
        else:
            self._add_files_btn = QPushButton("+")
        self._add_files_btn.setFixedSize(28, 28)
        self._add_files_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._add_files_btn.setToolTip("Додати файли")
        self._add_files_btn.clicked.connect(self._add_files)
        buttons_layout.addWidget(self._add_files_btn, 0)
        
        if HAS_QTA:
            folder_icon = qta.icon('fa5s.folder-plus', color='#ffffff')
            self._add_folder_btn = QPushButton(folder_icon, "")
        else:
            self._add_folder_btn = QPushButton("+F")
        self._add_folder_btn.setFixedSize(28, 28)
        self._add_folder_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._add_folder_btn.setToolTip("Додати папку")
        self._add_folder_btn.clicked.connect(self._add_folder)
        buttons_layout.addWidget(self._add_folder_btn, 0)
        
        if HAS_QTA:
            remove_icon = qta.icon('fa5s.minus', color='#ffffff')
            self._remove_track_btn = QPushButton(remove_icon, "")
        else:
            self._remove_track_btn = QPushButton("−")
        self._remove_track_btn.setFixedSize(28, 28)
        self._remove_track_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._remove_track_btn.setToolTip("Видалити")
        self._remove_track_btn.clicked.connect(self._remove_track)
        buttons_layout.addWidget(self._remove_track_btn, 0)
        
        if HAS_QTA:
            clear_icon = qta.icon('fa5s.times', color='#ffffff')
            self._clear_playlist_btn = QPushButton(clear_icon, "")
        else:
            self._clear_playlist_btn = QPushButton("×")
        self._clear_playlist_btn.setFixedSize(28, 28)
        self._clear_playlist_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._clear_playlist_btn.setToolTip("Очистити")
        self._clear_playlist_btn.clicked.connect(self._clear_playlist)
        buttons_layout.addWidget(self._clear_playlist_btn, 0)
        
        buttons_layout.addStretch()
        
        # Сортування компактно - фіксований розмір
        self._sort_combo = QComboBox()
        self._sort_combo.addItems(["Без сортування", "За назвою", "За виконавцем", "За альбомом"])
        self._sort_combo.currentIndexChanged.connect(self._sort_playlist)
        self._sort_combo.setFixedSize(130, 28)
        self._sort_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(self._sort_combo, 0)
        
        # Кнопки збереження/завантаження з іконками - фіксовані розміри
        if HAS_QTA:
            save_icon = qta.icon('fa5s.save', color='#ffffff')
            self._save_playlist_btn = QPushButton(save_icon, "")
        else:
            self._save_playlist_btn = QPushButton("S")
        self._save_playlist_btn.setFixedSize(28, 28)
        self._save_playlist_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._save_playlist_btn.setToolTip("Зберегти плейлист")
        self._save_playlist_btn.clicked.connect(self._save_playlist)
        buttons_layout.addWidget(self._save_playlist_btn, 0)
        
        if HAS_QTA:
            load_icon = qta.icon('fa5s.folder-open', color='#ffffff')
            self._load_playlist_btn = QPushButton(load_icon, "")
        else:
            self._load_playlist_btn = QPushButton("L")
        self._load_playlist_btn.setFixedSize(28, 28)
        self._load_playlist_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._load_playlist_btn.setToolTip("Завантажити плейлист")
        self._load_playlist_btn.clicked.connect(self._load_playlist)
        buttons_layout.addWidget(self._load_playlist_btn, 0)
        
        layout.addWidget(buttons_container, 0)
        
        return widget
    
    
    def _create_control_panel(self) -> QFrame:
        """Створює компактну панель кнопок управління відтворенням - всі контроли в одному рядку"""
        frame = QFrame()
        frame.setObjectName("controlPanel")
        frame.setFixedHeight(100)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(8)
        
        # Прогрес-бар з часом
        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(10)
        
        self._position_label = QLabel("0:00:00")
        self._position_label.setFixedWidth(60)
        self._position_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._position_label.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: 500;")
        self._position_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        progress_layout.addWidget(self._position_label, 0)
        
        # Слайдер прогресу з анімацією
        self._position_slider = QSlider(Qt.Orientation.Horizontal)
        self._position_slider.setObjectName("progressSlider")
        self._position_slider.setMinimum(0)
        self._position_slider.setMaximum(100)
        self._position_slider.setFixedHeight(6)
        self._position_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: #2a2a2a;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #7c3aed);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #6366f1;
                width: 12px;
                height: 12px;
                margin: -3px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #6366f1;
                transform: scale(1.2);
            }
        """)
        self._position_slider.sliderPressed.connect(self._on_position_slider_pressed)
        self._position_slider.sliderReleased.connect(self._on_position_slider_released)
        self._position_slider.valueChanged.connect(self._on_position_slider_changed)
        self._position_slider_pressed = False
        self._position_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        progress_layout.addWidget(self._position_slider, 1)
        
        self._duration_label = QLabel("0:00:00")
        self._duration_label.setFixedWidth(60)
        self._duration_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._duration_label.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: 500;")
        self._duration_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        progress_layout.addWidget(self._duration_label, 0)
        
        layout.addLayout(progress_layout, 0)
        
        # Всі кнопки в одному рядку
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 4, 0, 0)
        buttons_layout.setSpacing(10)
        
        # Кнопка меню плейлисту
        if HAS_QTA:
            playlist_icon = qta.icon('fa5s.list', color='#ffffff')
            self._playlist_btn = QPushButton(playlist_icon, "")
        else:
            self._playlist_btn = QPushButton("☰")
        self._playlist_btn.setFixedSize(28, 28)
        self._playlist_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 16px;
                padding: 0px;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: #222;
                transform: scale(0.95);
            }
        """)
        self._playlist_btn.setToolTip("Плейлист (Ctrl+L)")
        self._playlist_btn.clicked.connect(self._toggle_playlist)
        buttons_layout.addWidget(self._playlist_btn, 0)
        
        # Кнопка додавання файлів - компактна
        if HAS_QTA:
            add_icon = qta.icon('fa5s.plus', color='#ffffff')
            self._add_files_btn = QPushButton(add_icon, "")
        else:
            self._add_files_btn = QPushButton("+")
        self._add_files_btn.setFixedSize(28, 28)
        self._add_files_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 14px;
                padding: 0px;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: #222;
                transform: scale(0.95);
            }
        """)
        self._add_files_btn.setToolTip("Додати файли (Ctrl+O)")
        self._add_files_btn.clicked.connect(self._add_files)
        buttons_layout.addWidget(self._add_files_btn, 0)
        
        buttons_layout.addSpacing(8)
        
        # Попередній трек - компактний
        self._previous_btn = QPushButton("◀◀")
        self._previous_btn.setFixedSize(32, 32)
        self._previous_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: #222;
                transform: scale(0.95);
            }
        """)
        self._previous_btn.clicked.connect(self._player.previous)
        buttons_layout.addWidget(self._previous_btn, 0)
        
        # Play/Pause - трохи більша
        self._play_pause_btn = QPushButton("▶")
        self._play_pause_btn.setFixedSize(40, 40)
        self._play_pause_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                border: none;
                border-radius: 20px;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background: #7c3aed;
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background: #5b21b6;
                transform: scale(0.95);
            }
        """)
        self._play_pause_btn.clicked.connect(self._on_play_pause)
        buttons_layout.addWidget(self._play_pause_btn, 0)
        
        # Наступний трек - компактний
        self._next_btn = QPushButton("▶▶")
        self._next_btn.setFixedSize(32, 32)
        self._next_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: #222;
                transform: scale(0.95);
            }
        """)
        self._next_btn.clicked.connect(self._player.next)
        buttons_layout.addWidget(self._next_btn, 0)
        
        buttons_layout.addSpacing(8)
        
        # Shuffle - мінімалістична
        if HAS_QTA:
            shuffle_icon = qta.icon('fa5s.random', color='#ffffff')
            self._shuffle_btn = QPushButton(shuffle_icon, "")
        else:
            self._shuffle_btn = QPushButton("S")
        self._shuffle_btn.setFixedSize(28, 28)
        self._shuffle_btn.setCheckable(True)
        self._shuffle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #888;
                font-size: 12px;
                padding: 0px;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
                color: #ffffff;
                transform: scale(1.05);
            }
            QPushButton:checked {
                background: #6366f1;
                border: 1px solid #6366f1;
                color: #ffffff;
            }
            QPushButton:checked:hover {
                background: #7c3aed;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
        """)
        self._shuffle_btn.setToolTip("Shuffle")
        self._shuffle_btn.clicked.connect(self._on_shuffle_toggled)
        buttons_layout.addWidget(self._shuffle_btn, 0)
        
        # Repeat - мінімалістична
        if HAS_QTA:
            repeat_icon = qta.icon('fa5s.redo', color='#ffffff')
            self._repeat_btn = QPushButton(repeat_icon, "")
        else:
            self._repeat_btn = QPushButton("R")
        self._repeat_btn.setFixedSize(28, 28)
        self._repeat_btn.setCheckable(True)
        self._repeat_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #888;
                font-size: 12px;
                padding: 0px;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
                color: #ffffff;
                transform: scale(1.05);
            }
            QPushButton:checked {
                background: #6366f1;
                border: 1px solid #6366f1;
                color: #ffffff;
            }
            QPushButton:checked:hover {
                background: #7c3aed;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
        """)
        self._repeat_btn.setToolTip("Repeat: Off")
        self._repeat_btn.clicked.connect(self._on_repeat_clicked)
        buttons_layout.addWidget(self._repeat_btn, 0)
        
        buttons_layout.addStretch()
        
        # Гучність справа
        volume_container = QWidget()
        volume_container.setFixedWidth(150)
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(8)
        
        # Іконка гучності
        if HAS_QTA:
            volume_icon = qta.icon('fa5s.volume-up', color='#ffffff')
            volume_icon_label = QLabel()
            volume_icon_label.setPixmap(volume_icon.pixmap(20, 20))
        else:
            volume_icon_label = QLabel("🔊")
            volume_icon_label.setStyleSheet("color: #ffffff; font-size: 16px;")
        volume_icon_label.setFixedSize(24, 24)
        volume_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        volume_layout.addWidget(volume_icon_label, 0)
        
        # Слайдер гучності
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setMinimum(0)
        self._volume_slider.setMaximum(100)
        self._volume_slider.setValue(50)
        self._volume_slider.setFixedHeight(20)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        self._volume_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        volume_layout.addWidget(self._volume_slider, 1)
        
        buttons_layout.addWidget(volume_container, 0)
        
        layout.addLayout(buttons_layout, 0)
        
        return frame
    
    def _connect_signals(self):
        """Підключає сигнали програвача"""
        self._player.position_changed.connect(self._on_player_position_changed)
        self._player.duration_changed.connect(self._on_player_duration_changed)
        self._player.state_changed.connect(self._on_player_state_changed)
        self._player.track_changed.connect(self._on_track_changed)
        self._player.error_occurred.connect(self._on_player_error)
    
    def _setup_shortcuts(self):
        """Налаштовує гарячі клавіші"""
        # Play/Pause
        play_pause_shortcut = QShortcut(QKeySequence("Space"), self)
        play_pause_shortcut.activated.connect(self._on_play_pause)
        
        # Media Keys - Play/Pause
        media_play_shortcut = QShortcut(QKeySequence(Qt.Key.Key_MediaPlay), self)
        media_play_shortcut.activated.connect(self._on_play_pause)
        
        media_toggle_shortcut = QShortcut(QKeySequence(Qt.Key.Key_MediaTogglePlayPause), self)
        media_toggle_shortcut.activated.connect(self._on_play_pause)
        
        # Media Keys - Stop
        media_stop_shortcut = QShortcut(QKeySequence(Qt.Key.Key_MediaStop), self)
        media_stop_shortcut.activated.connect(self._on_stop)
        
        # Media Keys - Next
        media_next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_MediaNext), self)
        media_next_shortcut.activated.connect(self._player.next)
        
        # Media Keys - Previous
        media_prev_shortcut = QShortcut(QKeySequence(Qt.Key.Key_MediaPrevious), self)
        media_prev_shortcut.activated.connect(self._player.previous)
        
        # Stop
        stop_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        stop_shortcut.activated.connect(self._on_stop)
        
        # Next track
        next_shortcut = QShortcut(QKeySequence("Ctrl+Right"), self)
        next_shortcut.activated.connect(self._player.next)
        
        # Previous track
        prev_shortcut = QShortcut(QKeySequence("Ctrl+Left"), self)
        prev_shortcut.activated.connect(self._player.previous)
        
        # Volume up
        vol_up_shortcut = QShortcut(QKeySequence("Ctrl+Up"), self)
        vol_up_shortcut.activated.connect(self._volume_up)
        
        # Volume down
        vol_down_shortcut = QShortcut(QKeySequence("Ctrl+Down"), self)
        vol_down_shortcut.activated.connect(self._volume_down)
        
        # Seek forward (10 seconds)
        seek_forward_shortcut = QShortcut(QKeySequence("Right"), self)
        seek_forward_shortcut.activated.connect(self._seek_forward)
        
        # Seek backward (10 seconds)
        seek_backward_shortcut = QShortcut(QKeySequence("Left"), self)
        seek_backward_shortcut.activated.connect(self._seek_backward)
        
        # Open files
        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self._add_files)
        
        # Open playlist
        playlist_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        playlist_shortcut.activated.connect(self._toggle_playlist)
    
    def _volume_up(self):
        """Збільшує гучність"""
        current_vol = self._player.get_volume()
        new_vol = min(100, current_vol + 5)
        self._player.set_volume(new_vol)
        self._volume_slider.setValue(new_vol)
    
    def _volume_down(self):
        """Зменшує гучність"""
        current_vol = self._player.get_volume()
        new_vol = max(0, current_vol - 5)
        self._player.set_volume(new_vol)
        self._volume_slider.setValue(new_vol)
    
    def _seek_forward(self):
        """Переміщує на 10 секунд вперед"""
        current_pos = self._player.get_position()
        new_pos = current_pos + 10000  # 10 секунд
        duration = self._player.get_duration()
        if duration > 0:
            new_pos = min(duration, new_pos)
            self._player.set_position(new_pos)
    
    def _seek_backward(self):
        """Переміщує на 10 секунд назад"""
        current_pos = self._player.get_position()
        new_pos = max(0, current_pos - 10000)  # 10 секунд
        self._player.set_position(new_pos)
    
    def _load_saved_state(self):
        """Завантажує збережений стан при запуску"""
        from player.utils.state_manager import load_state
        
        # Завантажуємо налаштування
        settings = self._load_settings()
        resume = settings.get('resume', True)
        autoplay = settings.get('autoplay', False)
        
        state = load_state()
        if state:
            # Відновлюємо геометрію вікна
            geometry = state.get('window_geometry')
            if geometry:
                self.setGeometry(
                    geometry.get('x', 100),
                    geometry.get('y', 100),
                    geometry.get('width', 900),
                    geometry.get('height', 600)
                )
            # Відновлюємо плейлист
            if state.get('playlist'):
                self._player.get_playlist().add_tracks(state['playlist'])
                self._update_playlist_display()
            
            # Відновлюємо поточний трек
            current_index = state.get('current_index', -1)
            if 0 <= current_index < self._player.get_playlist().get_count():
                self._player.get_playlist().set_current_index(current_index)
                current = self._player.get_playlist().get_current_track()
                if current:
                    info = self._player.get_track_info(current)
                    self._track_title_label.setText(info['title'])
                    artist_text = info['artist'] if info['artist'] else "Невідомий виконавець"
                    album_text = info['album'] if info['album'] else ""
                    self._track_artist_label.setText(artist_text)
                    self._album_label.setText(album_text)
                    self._update_artwork(info.get('artwork'))
                    
                    # Відновлюємо позицію якщо увімкнено
                    if resume and state.get('position', 0) > 0:
                        self._player.load_file(current)
                        self._player.set_position(state.get('position', 0))
                    
                    # Автозапуск якщо увімкнено
                    if autoplay:
                        self._player.play()
            
            # Відновлюємо налаштування
            self._player.set_volume(state.get('volume', 50))
            self._volume_slider.setValue(state.get('volume', 50))
            repeat_mode = state.get('repeat', 0)
            self._player.set_repeat(repeat_mode)
            # Оновлюємо текст кнопки
            if repeat_mode == 0:
                self._repeat_btn.setText("Repeat: Off")
            elif repeat_mode == 1:
                self._repeat_btn.setText("Repeat: One")
            else:
                self._repeat_btn.setText("Repeat: All")
            self._player.set_shuffle(state.get('shuffle', False))
            self._shuffle_btn.setChecked(state.get('shuffle', False))
    
    def _load_settings(self) -> dict:
        """Завантажує налаштування з файлу"""
        try:
            from pathlib import Path
            import json
            
            settings_file = Path(__file__).parent.parent.parent / "settings.json"
            
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Значення за замовчуванням
                return {
                    'autoplay': False,
                    'resume': True,
                    'artwork_size': 150,
                    'autosave': True
                }
        except Exception as e:
            from ..utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Помилка завантаження налаштувань: {e}", exc_info=True)
            return {
                'autoplay': False,
                'resume': True,
                'artwork_size': 150,
                'autosave': True
            }
    
    def _show_settings(self):
        """Показує вікно налаштувань"""
        from .settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self)
        if dialog.exec():
            settings = dialog.get_settings()
            
            # Застосовуємо налаштування
            artwork_size = settings.get('artwork_size', 150)
            self._artwork_label.setFixedSize(artwork_size, artwork_size)
            
            # Оновлюємо обкладинку якщо потрібно
            current = self._player.get_playlist().get_current_track()
            if current:
                info = self._player.get_track_info(current)
                self._update_artwork(info.get('artwork'))
    
    def closeEvent(self, event):
        """Обробник закриття вікна - зберігає стан"""
        from player.utils.state_manager import save_state
        
        playlist = self._player.get_playlist()
        current_index = playlist.get_current_index()
        current_track = playlist.get_current_track()
        
        # Отримуємо позицію відтворення
        position = 0
        if current_track and self._player.get_state() == QMediaPlayer.PlaybackState.PlayingState:
            position = self._player.get_position()
        
        # Зберігаємо геометрію вікна
        geometry = {
            'x': self.x(),
            'y': self.y(),
            'width': self.width(),
            'height': self.height()
        }
        
        save_state(
            playlist=playlist.get_tracks(),
            current_index=current_index,
            volume=self._player.get_volume(),
            position=position,
            repeat=self._player.get_repeat(),
            shuffle=self._player.get_shuffle(),
            window_geometry=geometry
        )
        
        event.accept()
    
    def dragEnterEvent(self, event):
        """Обробник входу drag & drop"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Обробник drop - додає файли до плейлисту"""
        urls = event.mimeData().urls()
        if urls:
            audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.mp4'}
            file_paths = []
            
            for url in urls:
                file_path = url.toLocalFile()
                if Path(file_path).is_file():
                    # Перевіряємо розширення
                    if Path(file_path).suffix.lower() in audio_extensions:
                        file_paths.append(file_path)
                elif Path(file_path).is_dir():
                    # Якщо папка - додаємо всі аудіофайли
                    for ext in audio_extensions:
                        file_paths.extend([str(f) for f in Path(file_path).glob(f"*{ext}")])
                        file_paths.extend([str(f) for f in Path(file_path).glob(f"*{ext.upper()}")])
            
            if file_paths:
                added = self._player.get_playlist().add_tracks(file_paths)
                self._update_playlist_display()
                
                # Якщо це перший трек, встановлюємо його як поточний
                if self._player.get_playlist().get_current_index() == -1 and added > 0:
                    self._player.get_playlist().set_current_index(0)
                    current = self._player.get_playlist().get_current_track()
                    if current:
                        info = self._player.get_track_info(current)
                        self._track_title_label.setText(info['title'])
                        artist_text = info['artist'] if info['artist'] else "Невідомий виконавець"
                        album_text = info['album'] if info['album'] else ""
                        self._track_artist_label.setText(artist_text)
                        self._album_label.setText(album_text)
                        self._update_artwork(info.get('artwork'))
                
                QMessageBox.information(self, "Успіх", f"Додано {added} треків до плейлисту!")
            else:
                QMessageBox.warning(self, "Помилка", "Не знайдено аудіофайлів!")
    
    def _format_time(self, milliseconds: int) -> str:
        """Форматує час у формат M:SS або H:MM:SS"""
        total_seconds = milliseconds // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    @pyqtSlot(int)
    def _on_player_position_changed(self, position: int):
        """Обробник зміни позиції"""
        if not self._position_slider_pressed:
            duration = self._player.get_duration()
            if duration > 0:
                value = int((position / duration) * 100)
                self._position_slider.setValue(value)
                # Оновлюємо окремі мітки часу
                self._position_label.setText(self._format_time(position))
                if hasattr(self, '_duration_label'):
                    self._duration_label.setText(self._format_time(duration))
        
        # Оновлюємо заголовок з прогресом
        if self._player.get_state() == QMediaPlayer.PlaybackState.PlayingState:
            current_time = self._format_time(position)
            if self._original_title:
                title_text = self._original_title[:30] + "..." if len(self._original_title) > 30 else self._original_title
                self.setWindowTitle(f"▶ {title_text} - {current_time}")
            else:
                self.setWindowTitle(f"▶ Audio Player - {current_time}")
        else:
            self.setWindowTitle("Audio Player")
    
    @pyqtSlot(int)
    def _on_player_duration_changed(self, duration: int):
        """Обробник зміни тривалості"""
        if duration > 0:
            self._position_slider.setMaximum(100)
            # Оновлюємо окремі мітки часу
            self._position_label.setText(self._format_time(0))
            if hasattr(self, '_duration_label'):
                self._duration_label.setText(self._format_time(duration))
    
    @pyqtSlot(int)
    def _on_player_state_changed(self, state: int):
        """Обробник зміни стану програвача"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._play_pause_btn.setText("⏸")
            # Додаємо пульсацію обкладинки
            self._add_artwork_animation()
        else:
            self._play_pause_btn.setText("▶")
            # Видаляємо анімацію
            self._remove_artwork_animation()
    
    def _add_artwork_animation(self):
        """Додає пульсацію до обкладинки під час відтворення"""
        self._artwork_label.setStyleSheet("""
            QLabel {
                border: 3px solid #6366f1;
                border-radius: 8px;
                background: #1a1a1a;
                padding: 10px;
            }
        """)
    
    def _remove_artwork_animation(self):
        """Видаляє анімацію обкладинки"""
        self._artwork_label.setStyleSheet("""
            QLabel {
                border: 2px solid #2a2a2a;
                border-radius: 8px;
                background: #1a1a1a;
                padding: 10px;
            }
        """)
    
    @pyqtSlot(str)
    def _on_track_changed(self, file_path: str):
        """Обробник зміни треку"""
        info = self._player.get_track_info(file_path)
        
        # Зберігаємо оригінальну назву та запускаємо marquee якщо треба
        self._original_title = info['title']
        title_metrics = self._track_title_label.fontMetrics()
        title_width = title_metrics.horizontalAdvance(self._original_title)
        label_width = self._track_title_label.width()
        
        if title_width > label_width:
            # Довга назва - запускаємо marquee
            self._marquee_position = 0
            self._marquee_direction = 1
            self._marquee_timer.start(100)  # Оновлення кожні 100мс
        else:
            # Коротка назва - зупиняємо marquee
            self._marquee_timer.stop()
            self._track_title_label.setText(self._original_title)
        
        # Оновлюємо artist та album окремо для нового layout
        artist_text = info['artist'] if info['artist'] else "Невідомий виконавець"
        album_text = info['album'] if info['album'] else ""
        self._track_artist_label.setText(artist_text)
        self._album_label.setText(album_text)
        self._update_playlist_selection()
        self._update_artwork(info.get('artwork'))
    
    def _update_marquee(self):
        """Оновлює marquee анімацію для довгих назв"""
        if not self._original_title:
            return
        
        # Створюємо прокручуваний текст
        display_text = self._original_title + "   •   " + self._original_title
        
        # Оновлюємо позицію
        self._marquee_position += self._marquee_direction
        
        # Перевіряємо чи досягли кінця
        if self._marquee_position >= len(self._original_title) + 7:  # 7 = "   •   "
            self._marquee_position = 0
        
        # Відображаємо частину тексту
        visible_text = display_text[self._marquee_position:self._marquee_position + 50]
        self._track_title_label.setText(visible_text)
    
    @pyqtSlot(str)
    def _on_player_error(self, error: str):
        """Обробник помилок"""
        QMessageBox.warning(self, "Помилка", error)
    
    def _update_position(self):
        """Оновлює позицію відтворення"""
        # Оновлення відбувається через сигнали, але для надійності
        pass
    
    def _on_play_pause(self):
        """Обробник кнопки Play/Pause"""
        state = self._player.get_state()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()
    
    def _on_stop(self):
        """Обробник кнопки Stop"""
        self._player.stop()
    
    def _on_volume_changed(self, value: int):
        """Обробник зміни гучності"""
        self._player.set_volume(value)
        # Оновлюємо label якщо він існує (для старого дизайну)
        if hasattr(self, '_volume_label') and self._volume_label:
            self._volume_label.setText(f"{value}%")
    
    def _on_repeat_clicked(self):
        """Обробник кнопки Repeat - циклічно перемикає режими"""
        self._player.cycle_repeat_mode()
        mode = self._player.get_repeat()
        
        # Оновлюємо tooltip та стан кнопки
        if mode == 0:  # OFF
            self._repeat_btn.setToolTip("Repeat: Off")
            self._repeat_btn.setChecked(False)
        elif mode == 1:  # ONE
            self._repeat_btn.setToolTip("Repeat: One")
            self._repeat_btn.setChecked(True)
        else:  # ALL
            self._repeat_btn.setToolTip("Repeat: All")
            self._repeat_btn.setChecked(True)
    
    def _on_shuffle_toggled(self, checked: bool):
        """Обробник перемикача Shuffle"""
        self._player.set_shuffle(checked)
    
    def _on_position_slider_pressed(self):
        """Обробник натискання на слайдер позиції"""
        self._position_slider_pressed = True
    
    def _on_position_slider_released(self):
        """Обробник відпускання слайдера позиції"""
        self._position_slider_pressed = False
        duration = self._player.get_duration()
        if duration > 0:
            position = int((self._position_slider.value() / 100.0) * duration)
            self._player.set_position(position)
    
    def _on_position_slider_changed(self, value: int):
        """Обробник зміни значення слайдера позиції"""
        # Оновлюємо label під час перетягування
        if self._position_slider_pressed:
            duration = self._player.get_duration()
            if duration > 0:
                position = int((value / 100.0) * duration)
                # Оновлюємо окремі мітки часу
                self._position_label.setText(self._format_time(position))
                if hasattr(self, '_duration_label'):
                    self._duration_label.setText(self._format_time(duration))
    
    def _add_files(self):
        """Додає файли до плейлисту"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Оберіть аудіофайли",
            "",
            "Аудіо файли (*.mp3 *.wav *.flac *.ogg *.m4a *.aac *.wma *.mp4);;Всі файли (*.*)"
        )
        
        if file_paths:
            added = self._player.get_playlist().add_tracks(file_paths)
            self._update_playlist_display()
            
            # Якщо це перший трек, встановлюємо його як поточний
            if self._player.get_playlist().get_current_index() == -1 and added > 0:
                self._player.get_playlist().set_current_index(0)
                current = self._player.get_playlist().get_current_track()
                if current:
                    info = self._player.get_track_info(current)
                    self._track_title_label.setText(info['title'])
                    artist_text = info['artist'] if info['artist'] else "Невідомий виконавець"
                    album_text = info['album'] if info['album'] else ""
                    self._track_artist_label.setText(artist_text)
                    self._album_label.setText(album_text)
                    self._update_artwork(info.get('artwork'))
    
    def _add_folder(self):
        """Додає всі аудіофайли з папки"""
        folder_path = QFileDialog.getExistingDirectory(self, "Оберіть папку з аудіофайлами")
        
        if folder_path:
            audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.mp4'}
            audio_files = []
            
            for ext in audio_extensions:
                audio_files.extend(Path(folder_path).glob(f"*{ext}"))
                audio_files.extend(Path(folder_path).glob(f"*{ext.upper()}"))
            
            if audio_files:
                file_paths = [str(f) for f in audio_files]
                added = self._player.get_playlist().add_tracks(file_paths)
                self._update_playlist_display()
                
                if self._player.get_playlist().get_current_index() == -1 and added > 0:
                    self._player.get_playlist().set_current_index(0)
                    current = self._player.get_playlist().get_current_track()
                    if current:
                        info = self._player.get_track_info(current)
                        self._track_title_label.setText(info['title'])
                        self._track_artist_label.setText(f"{info['artist']} - {info['album']}")
                        self._update_artwork(info.get('artwork'))
            else:
                QMessageBox.information(self, "Інформація", "У вибраній папці не знайдено аудіофайлів")
    
    def _remove_track(self):
        """Видаляє вибраний трек з плейлисту"""
        current_item = self._playlist_widget.currentItem()
        if current_item:
            index = self._playlist_widget.row(current_item)
            if self._player.get_playlist().remove_track(index):
                self._update_playlist_display()
    
    def _clear_playlist(self):
        """Очищає плейлист"""
        reply = QMessageBox.question(
            self,
            "Підтвердження",
            "Ви впевнені, що хочете очистити плейлист?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._player.stop()
            self._player.get_playlist().clear()
            self._update_playlist_display()
            self._track_title_label.setText("Оберіть трек для відтворення")
            self._track_artist_label.setText("")
    
    def _update_playlist_display(self):
        """Оновлює відображення плейлисту"""
        # Перевіряємо чи існує віджет плейлисту (може не бути в новому дизайні)
        if not hasattr(self, '_playlist_widget') or not self._playlist_widget:
            return
        
        self._playlist_widget.clear()
        playlist = self._player.get_playlist()
        
        for i, track_path in enumerate(playlist.get_tracks()):
            track_name = Path(track_path).name
            item = QListWidgetItem(track_name)
            item.setData(Qt.ItemDataRole.UserRole, track_path)
            self._playlist_widget.addItem(item)
        
        self._update_playlist_selection()
    
    def _update_playlist_selection(self):
        """Оновлює виділення поточного треку в плейлисті"""
        # Перевіряємо чи існує віджет плейлисту
        if not hasattr(self, '_playlist_widget') or not self._playlist_widget:
            return
        
        current_index = self._player.get_playlist().get_current_index()
        if 0 <= current_index < self._playlist_widget.count():
            self._playlist_widget.setCurrentRow(current_index)
    
    def _update_artwork(self, artwork: QPixmap = None):
        """Оновлює обкладинку альбому"""
        from player.utils.artwork import create_placeholder_pixmap
        
        if artwork and not artwork.isNull():
            # Масштабуємо обкладинку до розміру label
            scaled = artwork.scaled(
                350, 350,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._artwork_label.setPixmap(scaled)
        else:
            # Встановлюємо placeholder
            placeholder = create_placeholder_pixmap(350)
            self._artwork_label.setPixmap(placeholder)
    
    def _show_playlist_context_menu(self, position: QPoint):
        """Показує контекстне меню для плейлисту"""
        item = self._playlist_widget.itemAt(position)
        if item is None:
            return
        
        menu = QMenu(self)
        
        # Дія: Відтворити
        play_action = menu.addAction("Відтворити")
        play_action.triggered.connect(lambda: self._on_playlist_item_double_clicked(item))
        
        menu.addSeparator()
        
        # Дія: Інформація
        info_action = menu.addAction("Інформація")
        info_action.triggered.connect(lambda: self._show_track_info(item))
        
        # Дія: Редагувати метадані
        edit_action = menu.addAction("Редагувати метадані")
        edit_action.triggered.connect(lambda: self._edit_track_metadata(item))
        
        menu.addSeparator()
        
        # Дія: Видалити
        remove_action = menu.addAction("Видалити")
        remove_action.triggered.connect(lambda: self._remove_track_from_context_menu(item))
        
        # Показуємо меню
        menu.exec(self._playlist_widget.mapToGlobal(position))
    
    def _show_track_info(self, item: QListWidgetItem):
        """Показує інформацію про трек"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if not file_path:
            return
        
        info = self._player.get_track_info(file_path)
        from pathlib import Path
        
        message = f"""
        <b>Назва:</b> {info['title']}<br>
        <b>Виконавець:</b> {info['artist']}<br>
        <b>Альбом:</b> {info['album']}<br>
        <b>Тривалість:</b> {self._format_time(info['duration'])}<br>
        <b>Файл:</b> {Path(file_path).name}<br>
        <b>Шлях:</b> {file_path}
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Інформація про трек")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(message)
        msg_box.exec()
    
    def _remove_track_from_context_menu(self, item: QListWidgetItem):
        """Видаляє трек з контекстного меню"""
        index = self._playlist_widget.row(item)
        if self._player.get_playlist().remove_track(index):
            self._update_playlist_display()
    
    def _filter_playlist(self, text: str):
        """Фільтрує плейлист за текстом пошуку"""
        search_text = text.lower().strip()
        
        for i in range(self._playlist_widget.count()):
            item = self._playlist_widget.item(i)
            if item:
                item_text = item.text().lower()
                file_path = item.data(Qt.ItemDataRole.UserRole)
                
                # Перевіряємо назву файлу та шлях
                matches = search_text in item_text
                if file_path:
                    matches = matches or search_text in file_path.lower()
                
                item.setHidden(not matches)
    
    def _save_playlist(self):
        """Зберігає поточний плейлист"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти плейлист",
            "",
            "M3U Playlist (*.m3u);;JSON Playlist (*.json);;Всі файли (*.*)"
        )
        
        if file_path:
            tracks = self._player.get_playlist().get_tracks()
            if not tracks:
                QMessageBox.information(self, "Інформація", "Плейлист порожній!")
                return
            
            from player.utils.playlist_io import save_m3u_playlist, save_json_playlist
            
            if file_path.endswith('.json'):
                # Зберігаємо як JSON
                metadata = {
                    'name': Path(file_path).stem,
                    'count': len(tracks)
                }
                success = save_json_playlist(file_path, tracks, metadata)
            else:
                # Зберігаємо як M3U (або додаємо розширення)
                if not file_path.endswith('.m3u'):
                    file_path += '.m3u'
                success = save_m3u_playlist(file_path, tracks)
            
            if success:
                self._save_recent_playlist(file_path)
                QMessageBox.information(self, "Успіх", f"Плейлист збережено!\n{len(tracks)} треків")
            else:
                QMessageBox.warning(self, "Помилка", "Не вдалося зберегти плейлист!")
    
    def _load_playlist(self):
        """Завантажує плейлист"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Завантажити плейлист",
            "",
            "Playlists (*.m3u *.json);;M3U Playlist (*.m3u);;JSON Playlist (*.json);;Всі файли (*.*)"
        )
        
        if file_path:
            from player.utils.playlist_io import load_m3u_playlist, load_json_playlist
            
            if file_path.endswith('.json'):
                tracks, metadata = load_json_playlist(file_path)
            else:
                tracks = load_m3u_playlist(file_path)
            
            if tracks:
                # Питаємо чи додати до поточного чи замінити
                reply = QMessageBox.question(
                    self,
                    "Завантаження плейлисту",
                    f"Знайдено {len(tracks)} треків.\nДодати до поточного плейлисту?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Cancel:
                    return
                
                if reply == QMessageBox.StandardButton.No:
                    # Замінюємо поточний плейлист
                    self._player.get_playlist().clear()
                    self._player.stop()
                
                # Додаємо треки
                added = self._player.get_playlist().add_tracks(tracks)
                self._update_playlist_display()
                
                if added > 0:
                    self._save_recent_playlist(file_path)
                    QMessageBox.information(self, "Успіх", f"Завантажено {added} треків!")
                    # Встановлюємо перший трек як поточний якщо плейлист був порожній
                    if self._player.get_playlist().get_current_index() == -1:
                        self._player.get_playlist().set_current_index(0)
                        current = self._player.get_playlist().get_current_track()
                        if current:
                            info = self._player.get_track_info(current)
                            self._track_title_label.setText(info['title'])
                            self._track_artist_label.setText(f"{info['artist']} - {info['album']}")
                            self._update_artwork(info.get('artwork'))
                else:
                    QMessageBox.warning(self, "Увага", "Не вдалося додати жодного треку!")
            else:
                QMessageBox.warning(self, "Помилка", "Не вдалося завантажити плейлист або він порожній!")
    
    def _on_playlist_reordered(self, parent=None, start=None, end=None, destination=None, row=None):
        """Обробник зміни порядку треків через drag & drop"""
        # Використовуємо QTimer для відкладеної обробки після завершення drag & drop
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._update_playlist_order)
    
    def _update_playlist_order(self):
        """Оновлює порядок треків в плейлисті після drag & drop"""
        playlist = self._player.get_playlist()
        
        # Отримуємо новий порядок з UI
        new_order = []
        for i in range(self._playlist_widget.count()):
            item = self._playlist_widget.item(i)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path:
                    new_order.append(file_path)
        
        # Перевіряємо чи порядок дійсно змінився
        current_tracks = playlist.get_tracks()
        if new_order != current_tracks and len(new_order) == len(current_tracks):
            current_track = playlist.get_current_track()
            
            # Оновлюємо плейлист
            playlist.clear()
            playlist.add_tracks(new_order)
            
            # Відновлюємо поточний індекс
            if current_track and current_track in new_order:
                new_index = new_order.index(current_track)
                playlist.set_current_index(new_index)
                self._update_playlist_selection()
    
    def _sort_playlist(self, index: int):
        """Сортує плейлист"""
        playlist = self._player.get_playlist()
        tracks = playlist.get_tracks()
        
        if not tracks:
            return
        
        current_track = playlist.get_current_track()
        current_index = playlist.get_current_index()
        
        if index == 0:  # Без сортування
            return
        elif index == 1:  # За назвою
            sorted_tracks = sorted(tracks, key=lambda x: Path(x).stem.lower())
        elif index == 2:  # За виконавцем
            sorted_tracks = sorted(tracks, key=lambda x: self._player.get_track_info(x).get('artist', '').lower())
        elif index == 3:  # За альбомом
            sorted_tracks = sorted(tracks, key=lambda x: self._player.get_track_info(x).get('album', '').lower())
        else:
            return
        
        # Оновлюємо плейлист
        playlist.clear()
        playlist.add_tracks(sorted_tracks)
        
        # Відновлюємо поточний трек
        if current_track and current_track in sorted_tracks:
            new_index = sorted_tracks.index(current_track)
            playlist.set_current_index(new_index)
        
        self._update_playlist_display()
    
    def _show_history(self):
        """Показує вікно з історією відтворення"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QShortcut
        from PyQt6.QtGui import QKeySequence
        from pathlib import Path
        
        history = self._player.get_history().get_recent(50)
        
        if not history:
            QMessageBox.information(self, "Історія", "Історія відтворення порожня")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Історія відтворення")
        dialog.setMinimumSize(650, 500)
        dialog.setStyleSheet("QDialog { background: #0f0f0f; }")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Заголовок
        title = QLabel(f"Нещодавно відтворені ({len(history)} треків)")
        title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Список історії
        history_list = QListWidget()
        history_list.setStyleSheet("""
            QListWidget {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                color: #ffffff;
                padding: 8px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background: #2a2a2a;
            }
            QListWidget::item:selected {
                background: #6366f1;
                color: #ffffff;
            }
        """)
        
        for entry in history:
            title_text = entry.get('title', Path(entry.get('file_path', '')).stem)
            artist_text = entry.get('artist', 'Невідомий виконавець')
            item_text = f"{title_text} - {artist_text}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, entry.get('file_path'))
            history_list.addItem(item)
        
        history_list.itemDoubleClicked.connect(lambda item: self._play_from_history(item))
        layout.addWidget(history_list)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        clear_btn = QPushButton("Очистити історію")
        clear_btn.setFixedHeight(32)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: #2a2a2a;
                border: 1px solid #6366f1;
            }
            QPushButton:pressed {
                background: #1a1a1a;
            }
        """)
        clear_btn.clicked.connect(lambda: self._clear_history(dialog))
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрити")
        close_btn.setFixedHeight(32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #4f46e5;
            }
            QPushButton:pressed {
                background: #3730a3;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Escape для закриття
        QShortcut(QKeySequence("Esc"), dialog).activated.connect(dialog.accept)
        
        dialog.exec()
    
    def _play_from_history(self, item: QListWidgetItem):
        """Відтворює трек з історії"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and Path(file_path).exists():
            # Додаємо до плейлисту якщо немає
            playlist = self._player.get_playlist()
            if file_path not in playlist.get_tracks():
                playlist.add_track(file_path)
                self._update_playlist_display()
            
            # Встановлюємо як поточний та відтворюємо
            index = playlist.get_tracks().index(file_path)
            playlist.set_current_index(index)
            self._player.load_file(file_path)
            self._player.play()
            self._on_track_changed(file_path)
    
    def _clear_history(self, dialog):
        """Очищає історію відтворення"""
        reply = QMessageBox.question(
            dialog,
            "Підтвердження",
            "Ви впевнені, що хочете очистити історію відтворення?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._player.get_history().clear()
            dialog.accept()
            QMessageBox.information(self, "Інформація", "Історія очищена")
    
    def _show_equalizer(self):
        """Показує діалог еквалайзера"""
        from .equalizer_dialog import EqualizerDialog
        dialog = EqualizerDialog(self)
        dialog.exec()
    
    def _toggle_playlist(self):
        """Відкриває вікно плейлисту"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Плейлист")
        dialog.setMinimumSize(700, 550)
        
        # Застосовуємо темну тему
        dialog.setStyleSheet("""
            QDialog {
                background: #0f0f0f;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Заголовок
        title_label = QLabel("Плейлист")
        title_label.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; background: transparent;")
        layout.addWidget(title_label, 0)
        
        # Пошук
        search_input = QLineEdit()
        search_input.setPlaceholderText("Пошук...")
        search_input.setFixedHeight(32)
        search_input.setStyleSheet("""
            QLineEdit {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 6px 10px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #6366f1;
                background: #252525;
            }
        """)
        search_input.textChanged.connect(self._filter_playlist)
        layout.addWidget(search_input, 0)
        
        # Ctrl+F фокусує пошук
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), dialog)
        search_shortcut.activated.connect(search_input.setFocus)
        
        # Список плейлисту
        playlist_list = QListWidget()
        playlist_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        playlist_list.itemDoubleClicked.connect(self._on_playlist_item_double_clicked)
        playlist_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        playlist_list.customContextMenuRequested.connect(self._show_playlist_context_menu)
        
        # Обробка клавіш для плейлисту
        def handle_playlist_keys(event):
            from PyQt6.QtCore import Qt
            if event.key() == Qt.Key.Key_Delete:
                # Delete - видалити трек
                current = playlist_list.currentItem()
                if current:
                    self._remove_track_from_list(playlist_list)
            elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                # Enter - відтворити трек
                current = playlist_list.currentItem()
                if current:
                    self._on_playlist_item_double_clicked(current)
            elif event.key() == Qt.Key.Key_Escape:
                # Escape - закрити діалог
                dialog.accept()
            else:
                QListWidget.keyPressEvent(playlist_list, event)
        
        playlist_list.keyPressEvent = handle_playlist_keys
        
        # Заповнюємо список
        playlist = self._player.get_playlist()
        for i, track_path in enumerate(playlist.get_tracks()):
            # Отримуємо інфо про трек
            info = self._player.get_track_info(track_path)
            duration_str = self._format_time(info.get('duration', 0))
            
            # Назва з тривалістю
            track_name = f"{Path(track_path).stem} ({duration_str})"
            item = QListWidgetItem(track_name)
            item.setData(Qt.ItemDataRole.UserRole, track_path)
            
            # Tooltip з повною інформацією
            bitrate = info.get('bitrate', 'Unknown')
            file_format = Path(track_path).suffix[1:].upper()
            tooltip = f"{Path(track_path).name}\n"
            tooltip += f"Виконавець: {info.get('artist', 'Невідомо')}\n"
            tooltip += f"Альбом: {info.get('album', 'Невідомо')}\n"
            tooltip += f"Формат: {file_format} • {bitrate}"
            item.setToolTip(tooltip)
            
            playlist_list.addItem(item)
        
        # Виділяємо поточний трек
        current_index = playlist.get_current_index()
        if 0 <= current_index < playlist_list.count():
            playlist_list.setCurrentRow(current_index)
        
        layout.addWidget(playlist_list, 1)
        
        # Компактні кнопки знизу
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Додати
        if HAS_QTA:
            add_icon = qta.icon('fa5s.plus', color='#ffffff')
            add_btn = QPushButton(add_icon, "")
        else:
            add_btn = QPushButton("+")
        add_btn.setFixedSize(32, 32)
        add_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
            }
        """)
        add_btn.setToolTip("Додати файли")
        add_btn.clicked.connect(self._add_files)
        buttons_layout.addWidget(add_btn)
        
        # Додати папку
        if HAS_QTA:
            folder_icon = qta.icon('fa5s.folder-plus', color='#ffffff')
            folder_btn = QPushButton(folder_icon, "")
        else:
            folder_btn = QPushButton("+F")
        folder_btn.setFixedSize(32, 32)
        folder_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
            }
        """)
        folder_btn.setToolTip("Додати папку")
        folder_btn.clicked.connect(self._add_folder)
        buttons_layout.addWidget(folder_btn)
        
        # Видалити
        if HAS_QTA:
            remove_icon = qta.icon('fa5s.minus', color='#ffffff')
            remove_btn = QPushButton(remove_icon, "")
        else:
            remove_btn = QPushButton("−")
        remove_btn.setFixedSize(32, 32)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
            }
        """)
        remove_btn.setToolTip("Видалити вибраний")
        remove_btn.clicked.connect(lambda: self._remove_track_from_list(playlist_list))
        buttons_layout.addWidget(remove_btn)
        
        # Очистити
        if HAS_QTA:
            clear_icon = qta.icon('fa5s.times', color='#ffffff')
            clear_btn = QPushButton(clear_icon, "")
        else:
            clear_btn = QPushButton("×")
        clear_btn.setFixedSize(32, 32)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ffffff;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #333;
                border: 1px solid #6366f1;
            }
        """)
        clear_btn.setToolTip("Очистити плейлист")
        clear_btn.clicked.connect(self._clear_playlist)
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        
        # Закрити
        close_btn = QPushButton("Закрити")
        close_btn.setFixedSize(80, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #7c3aed;
            }
            QPushButton:pressed {
                background: #5b21b6;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout, 0)
        
        dialog.exec()
    
    def _remove_track_from_list(self, playlist_widget):
        """Видаляє трек з плейлисту"""
        current_item = playlist_widget.currentItem()
        if current_item:
            index = playlist_widget.row(current_item)
            if self._player.get_playlist().remove_track(index):
                playlist_widget.takeItem(index)
                self._update_playlist_display()
    
    def _on_playlist_item_double_clicked(self, item: QListWidgetItem):
        """Обробник подвійного кліку на елемент плейлисту - відтворює трек"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            index = self._playlist_widget.row(item) if hasattr(self, '_playlist_widget') and self._playlist_widget else item.listWidget().row(item)
            self._player.get_playlist().set_current_index(index)
            self._player.load_file(file_path)
            self._player.play()
            self._on_track_changed(file_path)

