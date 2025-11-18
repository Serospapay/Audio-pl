"""
Audio Player - Головний файл запуску
"""
import sys
from PyQt6.QtWidgets import QApplication
from player.ui import MainWindow
from player.utils.logger import setup_logger, get_logger


def main():
    """Головна функція запуску програми"""
    # Налаштовуємо логування
    logger = setup_logger("AudioPlayer")
    logger.info("=" * 50)
    logger.info("Запуск Audio Player")
    logger.info("=" * 50)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Audio Player")
        app.setOrganizationName("AudioPlayer")
        
        logger.info("Створення головного вікна")
        window = MainWindow()
        window.show()
        logger.info("Головне вікно відображено")
        
        logger.info("Запуск головного циклу додатку")
        exit_code = app.exec()
        logger.info(f"Додаток завершено з кодом: {exit_code}")
        return exit_code
    except Exception as e:
        logger.critical(f"Критична помилка при запуску: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    main()

