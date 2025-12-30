import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

app = Flask(__name__)
# Настраиваем CORS для работы с мини-приложением
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Конфигурация
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
DATA_FILE = "/home/malollas/arrows_data.json"
CHANNEL_ID = "@arrows_game"
GAME_URL = "https://7fq259fwxr-byte.github.io/arrowgame/"

# ========== БАЗОВЫЕ ФУНКЦИИ ==========
def load_data():
    """Загружает данные из файла"""
    try:
        print(f"Пытаюсь загрузить данные из {DATA_FILE}")
        
        if not os.path.exists(DATA_FILE):
            print(f"Файл {DATA_FILE} не найден. Создаю пустую базу.")
            # Создаем пустой файл
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            return {}
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print("Файл пустой. Возвращаю пустой словарь.")
                return {}
            
            data = json.loads(content)
            print(f"Успешно загружено {len(data)} пользователей")
            return data
            
    except json.JSONDecodeError as e:
        print(f"Ошибка JSON в файле: {e}")
        print("Создаю новый файл с тестовыми данными...")
        # Создаем тестовые данные
        test_data = create_test_data()
        save_data(test_data)
        return test_data
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        traceback.print_exc()
        return {}

def create_test_data():
    """Создает тестовые данные"""
    return {
        "123456": {
            "username": "Игрок_Алексей",
            "score": 25,
            "games_played": 30,
            "coins": 150,
            "level": 26
        },
        "654321": {
            "username": "Профи_Мария",
            "score": 42,
            "games_played": 50,
            "coins": 300,
            "level": 43
        },
        "111111": {
            "username": "Новичок_Иван",
            "score": 5,
            "games_played": 8,
            "coins": 40,
            "level": 6
        }
    }

def save_data(data):
    """Сохраняет данные в файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(data)} пользователей")
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

def ensure_data_file():
    """Проверяет и создает файл данных если нужно"""
    try:
        if not os.path.exists(DATA_FILE):
            print(f"Файл {DATA_FILE} не существует. Создаю...")
            test_data = create_test_data()
            save_data(test_data)
            return True
        
        # Проверяем, что файл читается
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                print("Файл пустой. Заполняю тестовыми данными...")
                test_data = create_test_data()
                save_data(test_data)
        
        return True
    except Exception as e:
        print(f"Ошибка при проверке файла данных: {e}")
        return False

# ========== API ДЛЯ ИГРЫ ==========
@app.route('/api/get_user', methods=['POST'])
def get_user():
    """Получение данных пользователя"""
    print("\n=== API: GET_USER ===")
    try:
        data = request.get_json()
        print(f"Получены данные: {data}")
        
        user_id = str(data.get('user_id', '0'))
        username = data.get('username', 'Guest')
        first_name = data.get('first_name', '')
        
        print(f"User ID: {user_id}, Username: {username}")
        
        users = load_data()
        print(f"Загружено пользователей: {len(users)}")
        
        if user_id not in users:
            users[user_id] = {
                "username": username,
                "first_name": first_name,
                "score": 0,
                "games_played": 0,
                "coins": 0,
                "level": 1
            }
            save_data(users)
            print(f"Создан новый пользователь: {user_id}")
        
        user_data = users[user_id]
        print(f"Возвращаю данные: {user_data}")
        
        return jsonify({
            "success": True, 
            "user": user_data
        })
        
    except Exception as e:
        print(f"Ошибка в get_user: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@app.route('/api/update_score', methods=['POST'])
def update_score():
    """Обновление счета пользователя"""
    print("\n=== API: UPDATE_SCORE ===")
    try:
        data = request.get_json()
        print(f"Данные: {data}")
        
        user_id = str(data.get('user_id', '0'))
        username = data.get('username', 'Guest')
        new_level = int(data.get('level', 1))
        coins_earned = int(data.get('coins_earned', 0))
        
        print(f"Обновление для {user_id}: уровень={new_level}, монеты={coins_earned}")
        
        users = load_data()
        
        if user_id not in users:
            # Создаем нового пользователя
            users[user_id] = {
                "username": username,
                "score": new_level - 1,
                "games_played": 1,
                "coins": coins_earned,
                "level": new_level
            }
        else:
            # Обновляем существующего
            user = users[user_id]
            if new_level > user.get('level', 1):
                user['level'] = new_level
                user['score'] = new_level - 1
            
            user['coins'] = user.get('coins', 0) + coins_earned
            user['games_played'] = user.get('games_played', 0) + 1
            if username != 'Guest':
                user['username'] = username
        
        save_data(users)
        
        updated_user = users[user_id]
        print(f"Обновленный пользователь: {updated_user}")
        
        return jsonify({
            "success": True, 
            "coins": updated_user['coins'],
            "level": updated_user['level'],
            "score": updated_user['score']
        })
        
    except Exception as e:
        print(f"Ошибка в update_score: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получение таблицы лидеров для игры"""
    print("\n=== API: LEADERBOARD ===")
    try:
        # Сначала убедимся, что файл существует
        ensure_data_file()
        
        users = load_data()
        print(f"Всего пользователей: {len(users)}")
        
        # Преобразуем в список для сортировки
        leaderboard_list = []
        for user_id_str, user_data in users.items():
            try:
                # Пробуем преобразовать ID в число
                user_id_num = int(user_id_str)
            except:
                user_id_num = 0
            
            leaderboard_list.append({
                "user_id": user_id_num,
                "username": user_data.get("username", f"Player_{user_id_str}"),
                "score": user_data.get("score", 0),
                "level": user_data.get("level", 1),
                "coins": user_data.get("coins", 0)
            })
        
        # Сортируем по score (пройденные уровни)
        sorted_leaderboard = sorted(
            leaderboard_list,
            key=lambda x: x.get('score', 0),
            reverse=True
        )[:10]  # Только топ-10
        
        print(f"Лидерборд содержит {len(sorted_leaderboard)} игроков")
        for i, player in enumerate(sorted_leaderboard, 1):
            print(f"{i}. {player['username']} - {player['score']} уровней")
        
        return jsonify({
            "success": True, 
            "leaderboard": sorted_leaderboard
        })
        
    except Exception as e:
        print(f"Критическая ошибка в лидерборде: {e}")
        traceback.print_exc()
        # Возвращаем пустой лидерборд вместо ошибки 500
        return jsonify({
            "success": True, 
            "leaderboard": []
        })

@app.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    """Вебхук для Telegram бота"""
    print("\n=== TELEGRAM WEBHOOK ===")
    try:
        update = request.get_json()
        print(f"Получен update: {update}")
        
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_id = update["message"]["from"]["id"]
            username = update["message"]["from"].get("username", "Гость")
            text = update["message"]["text"]
            
            if text == "/start":
                print(f"Обработка /start от {user_id} ({username})")
                
                # Проверяем подписку
                try:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
                    params = {"chat_id": CHANNEL_ID, "user_id": user_id}
                    response = requests.get(url, params=params, timeout=5)
                    
                    is_member = False
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("ok"):
                            status = data["result"].get("status", "left")
                            is_member = status in ["creator", "administrator", "member"]
                except:
                    is_member = False
                
                if not is_member:
                    # Не подписан - просим подписаться
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": "📢 Подписаться", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"},
                            {"text": "✅ Проверить", "callback_data": "check_sub"}
                        ]]
                    }
                    
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": "⚠️ *Для использования бота нужно подписаться на канал @arrows_game*",
                            "parse_mode": "Markdown",
                            "reply_markup": keyboard
                        }
                    )
                else:
                    # Подписан - показываем меню
                    # Сохраняем пользователя
                    users = load_data()
                    user_key = str(user_id)
                    if user_key not in users:
                        users[user_key] = {
                            "username": username,
                            "score": 0,
                            "games_played": 0,
                            "coins": 0,
                            "level": 1
                        }
                        save_data(users)
                    
                    # Главное меню
                    keyboard = {
                        "inline_keyboard": [
                            [{"text": "🎮 Играть", "web_app": {"url": GAME_URL}}],
                            [
                                {"text": "📊 Статистика", "callback_data": "stats"},
                                {"text": "🏆 Топ игроков", "callback_data": "top"}
                            ],
                            [
                                {"text": "🛠 Поддержка", "url": "https://t.me/arrow_game_supprot_bot"}
                            ]
                        ]
                    }
                    
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": f"🎮 *Добро пожаловать, {username}!*\n\nВыберите действие:",
                            "parse_mode": "Markdown",
                            "reply_markup": keyboard
                        }
                    )
        
        elif "callback_query" in update:
            callback = update["callback_query"]
            callback_id = callback["id"]
            chat_id = callback["message"]["chat"]["id"]
            message_id = callback["message"]["message_id"]
            user_id = callback["from"]["id"]
            data = callback["data"]
            
            print(f"Callback: {data} от {user_id}")
            
            # Отвечаем на callback
            try:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                    json={"callback_query_id": callback_id}
                )
            except:
                pass
            
            if data == "check_sub":
                # Проверка подписки
                try:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
                    params = {"chat_id": CHANNEL_ID, "user_id": user_id}
                    response = requests.get(url, params=params, timeout=5)
                    
                    is_member = False
                    if response.status_code == 200:
                        resp_data = response.json()
                        if resp_data.get("ok"):
                            status = resp_data["result"].get("status", "left")
                            is_member = status in ["creator", "administrator", "member"]
                except:
                    is_member = False
                
                if is_member:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                        json={
                            "chat_id": chat_id,
                            "message_id": message_id,
                            "text": "✅ *Подписка подтверждена!*\n\nИспользуйте /start для доступа к меню.",
                            "parse_mode": "Markdown"
                        }
                    )
                else:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                        json={
                            "chat_id": chat_id,
                            "message_id": message_id,
                            "text": "❌ *Вы еще не подписались!*\n\nНажмите кнопку ниже, чтобы подписаться на @arrows_game",
                            "parse_mode": "Markdown",
                            "reply_markup": {
                                "inline_keyboard": [[
                                    {"text": "📢 Подписаться", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"},
                                    {"text": "✅ Проверить", "callback_data": "check_sub"}
                                ]]
                            }
                        }
                    )
            
            elif data == "stats":
                users = load_data()
                user_key = str(user_id)
                user = users.get(user_key, {})
                
                stats_text = f"""📊 *Ваша статистика:*

👤 Игрок: {user.get('username', 'Гость')}
🏆 Уровень: {user.get('level', 1)}
⭐ Очки: {user.get('score', 0)}
💰 Монеты: {user.get('coins', 0)}
🎮 Игр сыграно: {user.get('games_played', 0)}"""
                
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": stats_text,
                        "parse_mode": "Markdown",
                        "reply_markup": {
                            "inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]
                        }
                    }
                )
            
            elif data == "top":
                try:
                    users = load_data()
                    print(f"Пользователей для лидерборда: {len(users)}")
                    
                    if not users:
                        top_text = "🏆 *Топ игроков:*\n\nПока никто не играл. Будьте первым!"
                    else:
                        # Сортируем по score
                        sorted_users = sorted(
                            [(uid, data) for uid, data in users.items()],
                            key=lambda x: x[1].get('score', 0),
                            reverse=True
                        )[:10]
                        
                        top_text = "🏆 *Топ-10 игроков:*\n\n"
                        for i, (player_id, player_data) in enumerate(sorted_users, 1):
                            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                            name = player_data.get('username', f'Игрок_{player_id}')
                            score = player_data.get('score', 0)
                            top_text += f"{medal} {name} - {score} очков\n"
                    
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                        json={
                            "chat_id": chat_id,
                            "message_id": message_id,
                            "text": top_text,
                            "parse_mode": "Markdown",
                            "reply_markup": {
                                "inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]
                            }
                        }
                    )
                    
                except Exception as e:
                    print(f"Ошибка в лидерборде бота: {e}")
                    traceback.print_exc()
                    
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                        json={
                            "chat_id": chat_id,
                            "message_id": message_id,
                            "text": "❌ Ошибка загрузки лидерборда. Попробуйте позже.",
                            "parse_mode": "Markdown",
                            "reply_markup": {
                                "inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]
                            }
                        }
                    )
            
            elif data == "back":
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": "Нажмите /start чтобы открыть меню",
                        "parse_mode": "Markdown"
                    }
                )
        
        return jsonify({"ok": True}), 200
        
    except Exception as e:
        print(f"Ошибка в вебхуке: {e}")
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """Тестовый endpoint"""
    return jsonify({
        "success": True,
        "message": "API работает!",
        "data_file": DATA_FILE,
        "file_exists": os.path.exists(DATA_FILE)
    })

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Отладочная информация"""
    try:
        users = load_data()
        
        info = {
            "success": True,
            "data_file": DATA_FILE,
            "file_exists": os.path.exists(DATA_FILE),
            "file_size": os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0,
            "users_count": len(users),
            "users": users
        }
        
        return jsonify(info)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/reset', methods=['GET'])
def reset_data():
    """Сброс данных к тестовым (только для отладки)"""
    try:
        test_data = create_test_data()
        save_data(test_data)
        return jsonify({
            "success": True,
            "message": "Данные сброшены к тестовым",
            "users_count": len(test_data)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

# ========== УПРАВЛЕНИЕ ВЕБХУКОМ ==========
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука"""
    try:
        webhook_url = "https://malollas.pythonanywhere.com/api/telegram"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        response = requests.get(url)
        return response.text
    except Exception as e:
        return f"Ошибка: {str(e)}"

# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arrows Game Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #003366; }
            .endpoint {
                background: #f8f9fa;
                padding: 10px;
                margin: 10px 0;
                border-left: 4px solid #003366;
                font-family: monospace;
            }
            .btn {
                display: inline-block;
                background: #003366;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 5px;
            }
            .btn:hover { background: #002244; }
            .btn-success { background: #28a745; }
            .btn-danger { background: #dc3545; }
            pre {
                background: #2b2b2b;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                overflow: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Arrows Game Bot</h1>
            <p><strong>Статус:</strong> ✅ Активен</p>
            
            <h2>🔧 Управление вебхуком:</h2>
            <a href="/set_webhook" class="btn btn-success">Установить вебхук</a>
            
            <h2>🔍 Отладка:</h2>
            <a href="/api/test" class="btn">Тест API</a>
            <a href="/api/debug" class="btn">Информация о данных</a>
            <a href="/api/leaderboard" class="btn">Лидерборд (JSON)</a>
            <a href="/api/reset" class="btn btn-danger">Сбросить данные</a>
            
            <h2>📊 API Endpoints:</h2>
            <div class="endpoint">GET /api/test - Тест работы API</div>
            <div class="endpoint">POST /api/get_user - Получить данные пользователя</div>
            <div class="endpoint">POST /api/update_score - Обновить счет</div>
            <div class="endpoint">GET /api/leaderboard - Получить лидерборд</div>
            <div class="endpoint">POST /api/telegram - Вебхук Telegram</div>
            <div class="endpoint">GET /api/debug - Отладочная информация</div>
            
            <h2>📝 Проверка данных:</h2>
            <p>Файл данных: <code>""" + DATA_FILE + """</code></p>
            <p>Существует: <span id="file-status">Проверка...</span></p>
            
            <script>
                // Проверяем статус файла
                fetch('/api/debug')
                    .then(response => response.json())
                    .then(data => {
                        if(data.success) {
                            document.getElementById('file-status').innerHTML = 
                                '✅ Да (' + data.file_size + ' байт, ' + data.users_count + ' пользователей)';
                        } else {
                            document.getElementById('file-status').innerHTML = '❌ Ошибка: ' + data.error;
                        }
                    })
                    .catch(error => {
                        document.getElementById('file-status').innerHTML = '❌ Ошибка запроса';
                    });
            </script>
        </div>
    </body>
    </html>
    """

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Запуск Arrows Game Bot")
    print("=" * 60)
    
    # Проверяем и создаем файл данных
    print(f"📁 Файл данных: {DATA_FILE}")
    print(f"📝 Проверяю файл данных...")
    
    if ensure_data_file():
        print("✅ Файл данных готов")
    else:
        print("❌ Проблема с файлом данных")
    
    # Загружаем данные для проверки
    users = load_data()
    print(f"👥 Пользователей в базе: {len(users)}")
    
    print("=" * 60)
    print("🌐 Сервер запущен на http://0.0.0.0:5000")
    print("=" * 60)
    
    # Для PythonAnywhere используем app как WSGI приложение
    # В production это будет обрабатываться через uWSGI
    app.run(debug=False, host='0.0.0.0', port=5000)
