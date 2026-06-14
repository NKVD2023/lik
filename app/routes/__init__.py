# routes/__init__.py
from .blueprint import main_bp

# Безопасно загружаем все модули (они сами привяжутся к main_bp)
from . import pages, tasks, notes, api