"""
Система логування для програвача
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "AudioPlayer", log_file: str = None, level: int = logging.INFO):
    """
    Налаштовує логер для програвача
    
    Args:
        name: Ім'я логера
        log_file: Шлях до файлу логів (якщо None, використовується logs/app.log)
        level: Рівень логування
        
    Returns:
        Налаштований логер
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Якщо логер вже налаштований, повертаємо його
    if logger.handlers:
        return logger
    
    # Формат логів
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольний handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловий handler з ротацією
    if log_file is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # У файл пишемо все
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "AudioPlayer") -> logging.Logger:
    """
    Отримує логер (створює якщо не існує)
    
    Args:
        name: Ім'я логера
        
    Returns:
        Логер
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        setup_logger(name)
    return logger

