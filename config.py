import os

class Config:
    # Ключ для защиты сессий и данных (в разработке используется дефолтный)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-987654321'
    
    # Путь к базе данных SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///system.db'
    
    # Отключение отслеживания изменений объектов для экономии памяти
    SQLALCHEMY_TRACK_MODIFICATIONS = False