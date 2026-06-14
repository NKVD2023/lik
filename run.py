from app import create_app

# Создание экземпляра приложения через фабрику
app = create_app()

if __name__ == '__main__':
    # Запуск сервера в режиме отладки (debug=True)
    app.run(debug=True, host='127.0.0.1', port=5555)