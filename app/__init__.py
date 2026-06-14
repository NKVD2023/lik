from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# 1. Инициализируем базу данных
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'system.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'

    db.init_app(app)

    # 2. Регистрируем роуты
    from .routes.blueprint import main_bp
    app.register_blueprint(main_bp)
    
    # Обязательно загружаем файлы роутов, чтобы Flask увидел ваши страницы
    from . import routes

    # 3. При старте: создаем БД и синхронизируем с TXT файлами
    with app.app_context():
        db.create_all()
        
        # ВАЖНО: Импорт синхронизации должен быть именно ЗДЕСЬ, внутри контекста!
        from .services import run_full_two_way_sync
        run_full_two_way_sync()

    return app