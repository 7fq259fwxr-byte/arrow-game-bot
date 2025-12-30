import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Конфигурация
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
DATA_FILE = "/home/malollas/arrows_data.json"
CHANNEL_ID = "@arrows_game"
GAME_URL = "https://7fq259fwxr-byte.github.io/arrowgame/"

# ========== БАЗОВЫЕ ФУНКЦИИ ==========
def load_data():
    """Загружает данные из файла или создает тестовые"""
    try:
        if not os.path.exists(DATA_FILE):
            # Создаем пустые данные
            print(f"Файл {DATA_FILE} не существует, создаем пустой словарь")
            return {}
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Загружено {len(data)} пользователей из {DATA_FILE}")
            return data
    except json.JSONDecodeError as e:
        print(f"Ошибка JSON в файле {DATA_FILE}: {e}")
        return {}
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {}

def save_data(data):
    """Сохраняет данные в файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(data)} пользователей в {DATA_FILE}")
        return True
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")
        return False

# ========== ОСНОВНОЙ ВЕБХУК ==========
@app.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    try:
        update = request.get_json()
        
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            user_id = update["message"]["from"]["id"]
            username = update["message"]["from"].get("username", "Гость")
            
            if "text" in update["message"]:
                text = update["message"]["text"]
                
                if text == "/start":
                    # Проверяем подписку на канал
                    import requests
                    check_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
                    check_params = {
                        "chat_id": CHANNEL_ID,
                        "user_id": user_id
                    }
                    
                    try:
                        check_resp = requests.get(check_url, params=check_params, timeout=5)
                        is_member = False
                        
                        if check_resp.status_code == 200:
                            data = check_resp.json()
                            if data.get("ok"):
                                status = data["result"].get("status", "left")
                                if status in ["creator", "administrator", "member"]:
                                    is_member = True
                    except:
                        is_member = False
                    
                    if not is_member:
                        # Пользователь не подписан
                        keyboard = {
                            "inline_keyboard": [[
                                {
                                    "text": "📢 Подписаться", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"
                                },
                                {"text": "✅ Проверить", "callback_data": "check_sub"}
                            ]]
                        }
                        
                        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        send_data = {
                            "chat_id": chat_id,
                            "text": "⚠️ *Требуется подписка!*\n\nПодпишитесь на канал @arrows_game чтобы использовать бота.",
                            "parse_mode": "Markdown",
                            "reply_markup": keyboard
                        }
                        requests.post(send_url, json=send_data)
                    
                    else:
                        # Пользователь подписан - показываем меню
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
                                    {"text": "🛠 Поддержка", "url": "https://t.me/arrow_game_supprot_bot"},
                                    {"text": "💡 Идея", "url": "https://t.me/arrow_game_supprot_bot"}
                                ]
                            ]
                        }
                        
                        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        send_data = {
                            "chat_id": chat_id,
                            "text": f"🎮 *Добро пожаловать, {username}!*\n\nВыберите действие:",
                            "parse_mode": "Markdown",
                            "reply_markup": keyboard
                        }
                        requests.post(send_url, json=send_data)
        
        elif "callback_query" in update:
            # Обработка нажатий на кнопки
            import requests
            callback = update["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            message_id = callback["message"]["message_id"]
            user_id = callback["from"]["id"]
            data = callback["data"]
            
            # Отвечаем на callback
            ans_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
            ans_data = {"callback_query_id": callback["id"]}
            requests.post(ans_url, json=ans_data)
            
            if data == "check_sub":
                # Проверяем подписку
                check_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
                check_params = {"chat_id": CHANNEL_ID, "user_id": user_id}
                
                try:
                    check_resp = requests.get(check_url, params=check_params, timeout=5)
                    is_member = False
                    
                    if check_resp.status_code == 200:
                        resp_data = check_resp.json()
                        if resp_data.get("ok"):
                            status = resp_data["result"].get("status", "left")
                            if status in ["creator", "administrator", "member"]:
                                is_member = True
                except:
                    is_member = False
                
                if is_member:
                    # Обновляем сообщение
                    edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
                    edit_data = {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": "✅ *Подписка подтверждена!*\n\nИспользуйте /start для доступа к меню.",
                        "parse_mode": "Markdown"
                    }
                    requests.post(edit_url, json=edit_data)
                else:
                    edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
                    edit_data = {
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
                    requests.post(edit_url, json=edit_data)
            
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
                
                edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
                edit_data = {
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": stats_text,
                    "parse_mode": "Markdown",
                    "reply_markup": {
                        "inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]  # Простая кнопка назад
                    }
                }
                requests.post(edit_url, json=edit_data)
            
            elif data == "top":
                try:
                    users = load_data()
                    print(f"Загружено {len(users)} пользователей для лидерборда")
                    
                    # Создаем список кортежей (user_id, user_data)
                    users_list = list(users.items())
                    print(f"Список пользователей: {users_list}")
                    
                    # Сортируем по score
                    sorted_users = sorted(users_list, 
                                        key=lambda x: x[1].get('score', 0), 
                                        reverse=True)[:10]
                    
                    print(f"Отсортировано {len(sorted_users)} пользователей")
                    
                    top_text = "🏆 *Топ-10 игроков:*\n\n"
                    
                    if not sorted_users:
                        top_text += "Пока никто не играл. Будьте первым!"
                    else:
                        for i, (user_id_str, user) in enumerate(sorted_users, 1):
                            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                            username = user.get('username', f'Игрок_{user_id_str}')
                            if len(username) > 20:
                                username = username[:20] + "..."
                            score = user.get('score', 0)
                            top_text += f"{medal} {username} - {score} очков\n"
                    
                    print(f"Сформирован текст лидерборда: {top_text}")
                    
                    edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
                    edit_data = {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": top_text,
                        "parse_mode": "Markdown",
                        "reply_markup": {
                            "inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]
                        }
                    }
                    
                    response = requests.post(edit_url, json=edit_data, timeout=10)
                    print(f"Ответ от Telegram API при редактировании: {response.status_code}")
                    if response.status_code != 200:
                        print(f"Ошибка: {response.text}")
                        
                except Exception as e:
                    print(f"Ошибка при формировании лидерборда в боте: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # Отправляем сообщение об ошибке
                    edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
                    edit_data = {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": "❌ Ошибка загрузки лидерборда. Попробуйте позже.",
                        "parse_mode": "Markdown",
                        "reply_markup": {
                            "inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]
                        }
                    }
                    requests.post(edit_url, json=edit_data)
            
            elif data == "back":
                # Просто возвращаем к /start
                send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                send_data = {
                    "chat_id": chat_id,
                    "text": "Нажмите /start чтобы открыть меню",
                    "parse_mode": "Markdown"
                }
                requests.post(send_url, json=send_data)
        
        return jsonify({"ok": True}), 200
        
    except Exception as e:
        print(f"Ошибка в вебхуке: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

# ========== API ДЛЯ ИГРЫ ==========
@app.route('/api/get_user', methods=['POST'])
def get_user():
    try:
        data = request.get_json()
        user_id = str(data.get('user_id', 'unknown'))
        username = data.get('username', 'Guest')
        
        print(f"API get_user: получен запрос от user_id={user_id}, username={username}")
        
        users = load_data()
        print(f"Загружено {len(users)} пользователей из базы")
        
        if user_id not in users:
            users[user_id] = {
                "username": username,
                "score": 0,
                "games_played": 0,
                "coins": 0,
                "level": 1
            }
            save_data(users)
            print(f"Создан новый пользователь: {user_id}")
        
        user_data = users[user_id]
        print(f"Возвращаем данные пользователя: {user_data}")
        
        return jsonify({"success": True, "user": user_data})
    except Exception as e:
        print(f"Ошибка в get_user: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update_score', methods=['POST'])
def update_score():
    try:
        data = request.get_json()
        user_id = str(data.get('user_id'))
        username = data.get('username')
        new_level = data.get('level')
        coins_earned = data.get('coins_earned', 0)
        
        print(f"API update_score: user_id={user_id}, new_level={new_level}, coins={coins_earned}")
        
        users = load_data()
        
        if user_id in users:
            user = users[user_id]
            current_level = user.get('level', 1)
            
            # Обновляем только если новый уровень выше
            if new_level > current_level:
                user['level'] = new_level
                user['score'] = new_level - 1  # Количество пройденных уровней
            
            # Добавляем монеты
            user['coins'] = user.get('coins', 0) + coins_earned
            
            # Увеличиваем счетчик игр
            user['games_played'] = user.get('games_played', 0) + 1
            
            if username and username != 'Guest':
                user['username'] = username
            
            save_data(users)
            print(f"Обновлен пользователь {user_id}: уровень={user['level']}, монеты={user['coins']}, счет={user['score']}")
            
            return jsonify({
                "success": True, 
                "coins": user['coins'],
                "level": user['level'],
                "score": user['score']
            })
        else:
            print(f"Пользователь {user_id} не найден, создаем нового")
            users[user_id] = {
                "username": username or f"User_{user_id}",
                "score": new_level - 1 if new_level else 0,
                "games_played": 1,
                "coins": coins_earned,
                "level": new_level or 1
            }
            save_data(users)
            
            return jsonify({
                "success": True,
                "coins": coins_earned,
                "level": new_level or 1,
                "score": (new_level - 1) if new_level else 0
            })
    except Exception as e:
        print(f"Ошибка в update_score: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        print("API leaderboard: получен запрос на лидерборд")
        
        users = load_data()
        print(f"Всего пользователей в базе: {len(users)}")
        
        if not users:
            print("База пуста, возвращаем пустой лидерборд")
            return jsonify({
                "success": True, 
                "leaderboard": []
            })
        
        # Преобразуем в список для сортировки
        users_list = []
        for user_id_str, user_data in users.items():
            try:
                # Пытаемся преобразовать user_id в число
                user_id_int = int(user_id_str)
            except ValueError:
                # Если не получается, используем строку
                user_id_int = user_id_str
            
            users_list.append({
                "user_id": user_id_int,
                "username": user_data.get("username", f"Player_{user_id_str}"),
                "score": user_data.get("score", 0),
                "level": user_data.get("level", 1),
                "coins": user_data.get("coins", 0)
            })
        
        print(f"Преобразовано {len(users_list)} пользователей")
        
        # Сортируем по score (пройденные уровни)
        sorted_users = sorted(
            users_list,
            key=lambda x: x.get('score', 0),
            reverse=True
        )[:10]  # Берем топ-10
        
        print(f"Отсортировано {len(sorted_users)} пользователей для лидерборда")
        
        return jsonify({
            "success": True, 
            "leaderboard": sorted_users
        })
        
    except Exception as e:
        print(f"Критическая ошибка в get_leaderboard: {e}")
        import traceback
        traceback.print_exc()
        
        # Возвращаем пустой лидерборд вместо ошибки 500
        return jsonify({
            "success": True, 
            "leaderboard": []
        })

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        "success": True,
        "message": "API работает!",
        "timestamp": "2024-01-01 00:00:00"
    })

# ========== НАСТРОЙКА ВЕБХУКА ==========
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        webhook_url = "https://malollas.pythonanywhere.com/api/telegram"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        response = requests.get(url)
        return f"Вебхук установлен: {response.text}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

# ========== КОРНЕВОЙ МАРШРУТ ==========
@app.route('/')
def home():
    return """
    <html>
    <head><title>Arrows Game Bot</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>Бот Arrows Game работает!</h1>
        <p>Используйте /set_webhook для настройки.</p>
        <h2>API Endpoints:</h2>
        <ul>
            <li><strong>GET /api/test</strong> - Тест API</li>
            <li><strong>POST /api/get_user</strong> - Получить данные пользователя</li>
            <li><strong>POST /api/update_score</strong> - Обновить счет</li>
            <li><strong>GET /api/leaderboard</strong> - Получить лидерборд</li>
            <li><strong>POST /api/telegram</strong> - Вебхук Telegram</li>
        </ul>
        <p><a href="/set_webhook">Установить вебхук</a></p>
    </body>
    </html>
    """

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("Запуск Arrows Game Bot...")
    print(f"DATA_FILE: {DATA_FILE}")
    print(f"Существует ли файл: {os.path.exists(DATA_FILE)}")
    
    # Создаем тестовые данные, если файл не существует
    if not os.path.exists(DATA_FILE):
        print("Создаем тестовые данные...")
        test_data = {
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
        save_data(test_data)
        print("Тестовые данные созданы")
    
    # Проверяем загрузку данных
    users = load_data()
    print(f"Загружено пользователей: {len(users)}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
