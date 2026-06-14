# app/paths.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
NOTES_DIR = os.path.join(DATA_DIR, 'notes')
TASKS_DIR = os.path.join(DATA_DIR, 'tasks')

# Гарантируем, что папки существуют при старте системы
os.makedirs(NOTES_DIR, exist_ok=True)
os.makedirs(TASKS_DIR, exist_ok=True)