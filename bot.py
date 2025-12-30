import os
import json
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
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
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
                                {"text": "📢 Подписаться", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"},
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
                users = load_data()
                top_users = sorted(users.values(), key=lambda x: x.get('score', 0), reverse=True)[:10]
                
                top_text = "🏆 *Топ-10 игроков:*\n\n"
                for i, user in enumerate(top_users, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    top_text += f"{medal} {user.get('username', 'Гость')} - {user.get('score', 0)} очков\n"
                
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
        print(f"Ошибка в вебхуке: {str(e)}")  # Для логов PythonAnywhere
        return jsonify({"ok": False, "error": str(e)}), 500

# ========== API ДЛЯ ИГРЫ (старое) ==========
@app.route('/api/get_user', methods=['POST'])
def get_user():
    try:
        data = request.get_json()
        user_id = str(data.get('user_id', 'unknown'))
        username = data.get('username', 'Guest')
        
        users = load_data()
        
        if user_id not in users:
            users[user_id] = {
                "username": username,
                "score": 0,
                "games_played": 0,
                "coins": 0,
                "level": 1
            }
            save_data(users)
        
        return jsonify({"success": True, "user": users[user_id]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        "success": True,
        "message": "API работает!",
        "timestamp": "2024-01-01 00:00:00"
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    users = load_data()
    sorted_users = sorted(users.values(), key=lambda x: x.get('score', 0), reverse=True)[:10]
    return jsonify(sorted_users)

# ========== НАСТРОЙКА ВЕБХУКА ==========
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        import requests
        webhook_url = "https://malollas.pythonanywhere.com/api/telegram"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        response = requests.get(url)
        return response.text
    except Exception as e:
        return f"Ошибка: {str(e)}"

# ========== КОРНЕВОЙ МАРШРУТ ==========
@app.route('/')
def home():
    return "Бот Arrows Game работает! Используйте /set_webhook для настройки."

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    app.run(debug=False)
