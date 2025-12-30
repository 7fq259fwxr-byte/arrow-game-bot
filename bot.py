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
    if not os.path.exists(DATA_FILE):
        # Создаем тестовых пользователей для демонстрации
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
            },
            "222222": {
                "username": "Чемпион_Ольга",
                "score": 68,
                "games_played": 75,
                "coins": 500,
                "level": 69
            },
            "333333": {
                "username": "Эксперт_Дмитрий",
                "score": 35,
                "games_played": 40,
                "coins": 220,
                "level": 36
            }
        }
        
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            return test_data
        except Exception as e:
            print(f"Ошибка создания тестовых данных: {e}")
            return {}
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {}

def save_data(data):
    """Сохраняет данные в файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")
        return False

def check_channel_subscription(user_id):
    """Проверяет подписку пользователя на канал"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
        params = {
            "chat_id": CHANNEL_ID,
            "user_id": user_id
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                status = data["result"].get("status", "left")
                return status in ["creator", "administrator", "member"]
        return False
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

def send_telegram_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    """Отправляет сообщение через Telegram API"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        response = requests.post(url, json=data, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return None

def edit_telegram_message(chat_id, message_id, text, reply_markup=None, parse_mode="Markdown"):
    """Редактирует сообщение через Telegram API"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        response = requests.post(url, json=data, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Ошибка редактирования сообщения: {e}")
        return None

# ========== ОСНОВНОЙ ВЕБХУК ==========
@app.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    """Обработчик вебхука от Telegram"""
    try:
        update = request.get_json()
        print(f"Получен вебхук: {update}")  # Логируем полученный вебхук
        
        if not update:
            return jsonify({"ok": False, "error": "Empty update"}), 400
        
        # Обработка команды /start из сообщения
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_id = update["message"]["from"]["id"]
            username = update["message"]["from"].get("username", f"user_{user_id}")
            first_name = update["message"]["from"].get("first_name", "")
            text = update["message"]["text"]
            
            if text == "/start" or text == "/start@arrows_pro_bot":
                print(f"Обработка /start от пользователя {user_id} ({username})")
                
                # Проверяем подписку
                is_member = check_channel_subscription(user_id)
                print(f"Подписка пользователя {user_id}: {is_member}")
                
                if not is_member:
                    # Пользователь не подписан - отправляем сообщение с требованием подписки
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": "📢 Подписаться на канал", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"},
                            {"text": "✅ Я подписался", "callback_data": f"check_sub_{user_id}"}
                        ]]
                    }
                    
                    message = f"""⚠️ *Требуется подписка!*

Для использования бота *Arrows Game* необходимо подписаться на наш канал:

📢 *{CHANNEL_ID}*

После подписки нажмите кнопку *«Я подписался»*."""
                    
                    result = send_telegram_message(
                        chat_id=chat_id,
                        text=message,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                    
                    if result:
                        print(f"Отправлено сообщение о подписке пользователю {user_id}")
                    else:
                        print(f"Ошибка отправки сообщения пользователю {user_id}")
                    
                else:
                    # Пользователь подписан - показываем главное меню
                    # Сохраняем/обновляем пользователя
                    users = load_data()
                    user_key = str(user_id)
                    
                    if user_key not in users:
                        users[user_key] = {
                            "username": username,
                            "first_name": first_name,
                            "score": 0,
                            "games_played": 0,
                            "coins": 0,
                            "level": 1
                        }
                        save_data(users)
                        print(f"Создан новый пользователь: {user_id} ({username})")
                    
                    # Главное меню
                    keyboard = {
                        "inline_keyboard": [
                            [{"text": "🎮 Играть в Arrows", "web_app": {"url": GAME_URL}}],
                            [
                                {"text": "📊 Моя статистика", "callback_data": "stats"},
                                {"text": "🏆 Топ игроков", "callback_data": "top"}
                            ],
                            [
                                {"text": "🛠 Поддержка", "url": "https://t.me/arrow_game_supprot_bot"},
                                {"text": "📢 Наш канал", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"}
                            ]
                        ]
                    }
                    
                    welcome_text = f"""🎮 *Добро пожаловать в Arrows Game, {first_name or username}!*

*Arrows* — это захватывающая игра на логику и реакцию, где нужно правильно расставлять стрелки.

✨ *Возможности:*
• 🎮 Увлекательная игра с множеством уровней
• 📊 Статистика и достижения
• 🏆 Таблица лидеров
• 💰 Внутриигровая валюта
• 🛠 Ежедневные обновления

*Выберите действие:*"""
                    
                    result = send_telegram_message(
                        chat_id=chat_id,
                        text=welcome_text,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                    
                    if result:
                        print(f"Отправлено приветственное сообщение пользователю {user_id}")
                    else:
                        print(f"Ошибка отправки приветственного сообщения пользователю {user_id}")
        
        # Обработка callback-запросов (нажатия на кнопки)
        elif "callback_query" in update:
            callback = update["callback_query"]
            callback_id = callback["id"]
            chat_id = callback["message"]["chat"]["id"]
            message_id = callback["message"]["message_id"]
            user_id = callback["from"]["id"]
            data = callback["data"]
            
            print(f"Обработка callback: {data} от пользователя {user_id}")
            
            # Отвечаем на callback (убираем "часики")
            try:
                answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
                answer_data = {"callback_query_id": callback_id}
                requests.post(answer_url, json=answer_data, timeout=5)
            except:
                pass
            
            # Проверка подписки
            if data.startswith("check_sub_"):
                check_user_id = data.replace("check_sub_", "")
                
                if str(user_id) == check_user_id:
                    is_member = check_channel_subscription(user_id)
                    
                    if is_member:
                        # Пользователь подписался - показываем меню
                        users = load_data()
                        user_key = str(user_id)
                        username = callback["from"].get("username", f"user_{user_id}")
                        first_name = callback["from"].get("first_name", "")
                        
                        if user_key not in users:
                            users[user_key] = {
                                "username": username,
                                "first_name": first_name,
                                "score": 0,
                                "games_played": 0,
                                "coins": 0,
                                "level": 1
                            }
                            save_data(users)
                        
                        keyboard = {
                            "inline_keyboard": [
                                [{"text": "🎮 Играть в Arrows", "web_app": {"url": GAME_URL}}],
                                [
                                    {"text": "📊 Моя статистика", "callback_data": "stats"},
                                    {"text": "🏆 Топ игроков", "callback_data": "top"}
                                ]
                            ]
                        }
                        
                        success_text = f"""✅ *Подписка подтверждена!*

Добро пожаловать в *Arrows Game*, {first_name or username}!

Теперь вы можете наслаждаться игрой и соревноваться с другими игроками.

*Выберите действие:*"""
                        
                        edit_telegram_message(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=success_text,
                            reply_markup=keyboard,
                            parse_mode="Markdown"
                        )
                    else:
                        # Пользователь все еще не подписан
                        keyboard = {
                            "inline_keyboard": [[
                                {"text": "📢 Подписаться на канал", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"},
                                {"text": "✅ Я подписался", "callback_data": f"check_sub_{user_id}"}
                            ]]
                        }
                        
                        error_text = """❌ *Подписка не обнаружена!*

Пожалуйста, убедитесь, что вы подписались на канал:

📢 *@arrows_game*

После подписки нажмите кнопку *«Я подписался»* еще раз."""
                        
                        edit_telegram_message(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=error_text,
                            reply_markup=keyboard,
                            parse_mode="Markdown"
                        )
            
            # Статистика
            elif data == "stats":
                users = load_data()
                user_key = str(user_id)
                user = users.get(user_key, {})
                
                stats_text = f"""📊 *Ваша статистика в Arrows Game:*

👤 *Игрок:* {user.get('username', f'user_{user_id}')}
🏆 *Уровень:* {user.get('level', 1)}
⭐ *Пройдено уровней:* {user.get('score', 0)}
💰 *Монеты:* {user.get('coins', 0)}
🎮 *Игр сыграно:* {user.get('games_played', 0)}

*Продолжайте играть, чтобы улучшить свои показатели!*"""
                
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🎮 Продолжить игру", "web_app": {"url": GAME_URL}}],
                        [{"text": "🔙 Назад в меню", "callback_data": "back_to_menu"}]
                    ]
                }
                
                edit_telegram_message(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=stats_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            
            # Топ игроков
            elif data == "top":
                users = load_data()
                
                # Сортируем игроков по количеству пройденных уровней (score)
                top_players = sorted(
                    [(uid, data) for uid, data in users.items()],
                    key=lambda x: x[1].get('score', 0),
                    reverse=True
                )[:10]
                
                top_text = "🏆 *Топ-10 игроков Arrows Game:*\n\n"
                
                for i, (player_id, player_data) in enumerate(top_players, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    player_name = player_data.get('username', f'Игрок_{player_id}')
                    if len(player_name) > 15:
                        player_name = player_name[:15] + "..."
                    
                    score = player_data.get('score', 0)
                    level = player_data.get('level', 1)
                    
                    top_text += f"{medal} *{player_name}*\n"
                    top_text += f"   Уровней: {score} | Текущий: {level}\n\n"
                
                if not top_players:
                    top_text = "🏆 *Таблица лидеров пуста!*\n\nБудьте первым, кто сыграет в Arrows Game!"
                
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🎮 Играть и попасть в топ", "web_app": {"url": GAME_URL}}],
                        [{"text": "🔙 Назад в меню", "callback_data": "back_to_menu"}]
                    ]
                }
                
                edit_telegram_message(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=top_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            
            # Назад в меню
            elif data == "back_to_menu":
                username = callback["from"].get("username", f"user_{user_id}")
                first_name = callback["from"].get("first_name", "")
                
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🎮 Играть в Arrows", "web_app": {"url": GAME_URL}}],
                        [
                            {"text": "📊 Моя статистика", "callback_data": "stats"},
                            {"text": "🏆 Топ игроков", "callback_data": "top"}
                        ],
                        [
                            {"text": "🛠 Поддержка", "url": "https://t.me/arrow_game_supprot_bot"},
                            {"text": "📢 Наш канал", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"}
                        ]
                    ]
                }
                
                menu_text = f"""🎮 *Меню Arrows Game*

Привет, {first_name or username}! Выберите действие:"""
                
                edit_telegram_message(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=menu_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
        
        return jsonify({"ok": True}), 200
        
    except Exception as e:
        print(f"❌ Критическая ошибка в вебхуке: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

# ========== API ДЛЯ ИГРЫ ==========
@app.route('/api/get_user', methods=['POST'])
def get_user():
    """Получение данных пользователя для игры"""
    try:
        data = request.get_json()
        user_id = str(data.get('user_id', 'unknown'))
        username = data.get('username', 'Guest')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        print(f"API: Получение пользователя {user_id} ({username})")
        
        users = load_data()
        
        if user_id not in users:
            users[user_id] = {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "score": 0,
                "games_played": 0,
                "coins": 0,
                "level": 1
            }
            save_data(users)
            print(f"API: Создан новый пользователь {user_id}")
        
        return jsonify({
            "success": True, 
            "user": users[user_id]
        })
    except Exception as e:
        print(f"API Ошибка get_user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update_score', methods=['POST'])
def update_score():
    """Обновление счета пользователя"""
    try:
        data = request.get_json()
        user_id = str(data.get('user_id'))
        username = data.get('username')
        new_level = data.get('level', 1)
        coins_earned = data.get('coins_earned', 0)
        
        print(f"API: Обновление счета для {user_id}, уровень: {new_level}, монеты: {coins_earned}")
        
        users = load_data()
        
        if user_id in users:
            user = users[user_id]
            old_level = user.get('level', 1)
            
            # Обновляем только если новый уровень больше старого
            if new_level > old_level:
                user['level'] = new_level
                user['score'] = new_level - 1  # Количество пройденных уровней
            
            # Добавляем монеты
            user['coins'] = user.get('coins', 0) + coins_earned
            
            # Увеличиваем счетчик игр
            user['games_played'] = user.get('games_played', 0) + 1
            
            if username:
                user['username'] = username
            
            save_data(users)
            print(f"API: Обновлен пользователь {user_id}, новый уровень: {user['level']}, монеты: {user['coins']}")
            
            return jsonify({
                "success": True, 
                "coins": user['coins'],
                "level": user['level'],
                "score": user['score']
            })
        else:
            print(f"API: Пользователь {user_id} не найден")
            return jsonify({"success": False, "error": "User not found"}), 404
    except Exception as e:
        print(f"API Ошибка update_score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получение таблицы лидеров"""
    try:
        print("API: Запрос лидерборда")
        users = load_data()
        
        # Преобразуем данные для лидерборда
        leaderboard_data = []
        for user_id_str, user_data in users.items():
            try:
                user_id_int = int(user_id_str)
            except:
                user_id_int = 0
            
            leaderboard_data.append({
                "user_id": user_id_int,
                "username": user_data.get("username", f"Player{user_id_str}"),
                "score": user_data.get("score", 0),
                "level": user_data.get("level", 1),
                "coins": user_data.get("coins", 0)
            })
        
        # Сортируем по количеству пройденных уровней (score)
        sorted_users = sorted(
            leaderboard_data,
            key=lambda x: x.get('score', 0),
            reverse=True
        )[:10]
        
        print(f"API: Лидерборд содержит {len(sorted_users)} игроков")
        
        return jsonify({
            "success": True, 
            "leaderboard": sorted_users
        })
        
    except Exception as e:
        print(f"API Ошибка лидерборда: {e}")
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """Тестовый endpoint для проверки работы API"""
    return jsonify({
        "success": True,
        "message": "Arrows Game API работает!",
        "timestamp": "2024-01-01 00:00:00",
        "endpoints": {
            "/api/get_user": "POST - получение данных пользователя",
            "/api/update_score": "POST - обновление счета",
            "/api/leaderboard": "GET - таблица лидеров",
            "/api/telegram": "POST - вебхук Telegram бота"
        }
    })

# ========== НАСТРОЙКА ВЕБХУКА ==========
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука для Telegram бота"""
    try:
        webhook_url = "https://malollas.pythonanywhere.com/api/telegram"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        response = requests.get(url)
        
        result = response.json()
        print(f"Результат установки вебхука: {result}")
        
        if result.get('ok'):
            return f"""
            <html>
            <head><title>Webhook установлен</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>✅ Вебхук успешно установлен!</h1>
                <p><strong>URL:</strong> {webhook_url}</p>
                <p><strong>Результат:</strong> {result.get('description', 'Unknown')}</p>
                <p><a href="/">Вернуться на главную</a></p>
            </body>
            </html>
            """
        else:
            return f"""
            <html>
            <head><title>Ошибка установки вебхука</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>❌ Ошибка установки вебхука!</h1>
                <p><strong>Ошибка:</strong> {result.get('description', 'Unknown')}</p>
                <p><a href="/">Вернуться на главную</a></p>
            </body>
            </html>
            """
    except Exception as e:
        return f"""
        <html>
        <head><title>Ошибка</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>❌ Ошибка установки вебхука!</h1>
            <p><strong>Исключение:</strong> {str(e)}</p>
            <p><a href="/">Вернуться на главную</a></p>
        </body>
        </html>
        """

@app.route('/remove_webhook', methods=['GET'])
def remove_webhook():
    """Удаление вебхука"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        response = requests.get(url)
        result = response.json()
        
        return f"""
        <html>
        <head><title>Webhook удален</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>🗑 Вебхук удален</h1>
            <p><strong>Результат:</strong> {result.get('description', 'Unknown')}</p>
            <p><a href="/set_webhook">Установить вебхук</a> | <a href="/">На главную</a></p>
        </body>
        </html>
        """
    except Exception as e:
        return f"Ошибка удаления вебхука: {str(e)}"

@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    """Информация о текущем вебхуке"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
        response = requests.get(url)
        result = response.json()
        
        info_html = "<h1>Информация о вебхуке</h1><pre>"
        info_html += json.dumps(result, indent=2, ensure_ascii=False)
        info_html += "</pre>"
        info_html += '<p><a href="/set_webhook">Установить вебхук</a> | <a href="/remove_webhook">Удалить вебхук</a> | <a href="/">На главную</a></p>'
        
        return info_html
    except Exception as e:
        return f"Ошибка получения информации о вебхуке: {str(e)}"

# ========== КОРНЕВОЙ МАРШРУТ ==========
@app.route('/')
def home():
    """Главная страница с информацией о боте"""
    return """
    <html>
    <head>
        <title>Arrows Game Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #003366;
                border-bottom: 2px solid #003366;
                padding-bottom: 10px;
            }
            h2 {
                color: #003366;
            }
            .status {
                background: #e8f4f8;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #003366;
            }
            .endpoint {
                background: #f9f9f9;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
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
                transition: background 0.3s;
            }
            .btn:hover {
                background: #002244;
            }
            .btn-success {
                background: #2ecc71;
            }
            .btn-success:hover {
                background: #27ae60;
            }
            .btn-danger {
                background: #e74c3c;
            }
            .btn-danger:hover {
                background: #c0392b;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Arrows Game Bot</h1>
            
            <div class="status">
                <h2>Статус бота: <span style="color: #2ecc71;">✅ Активен</span></h2>
                <p>Бот для игры Arrows Game с таблицей лидеров и статистикой.</p>
            </div>
            
            <h2>📊 API Endpoints:</h2>
            <div class="endpoint">
                <strong>GET /api/test</strong> - Тест API
            </div>
            <div class="endpoint">
                <strong>POST /api/get_user</strong> - Получение данных пользователя
            </div>
            <div class="endpoint">
                <strong>POST /api/update_score</strong> - Обновление счета
            </div>
            <div class="endpoint">
                <strong>GET /api/leaderboard</strong> - Таблица лидеров
            </div>
            <div class="endpoint">
                <strong>POST /api/telegram</strong> - Вебхук Telegram бота
            </div>
            
            <h2>⚙️ Управление вебхуком:</h2>
            <a href="/set_webhook" class="btn btn-success">Установить вебхук</a>
            <a href="/remove_webhook" class="btn btn-danger">Удалить вебхук</a>
            <a href="/webhook_info" class="btn">Информация о вебхуке</a>
            
            <h2>🔗 Ссылки:</h2>
            <p><a href="https://t.me/arrows_pro_bot" target="_blank">Telegram бот</a></p>
            <p><a href="https://t.me/arrows_game" target="_blank">Наш канал</a></p>
            <p><a href="https://7fq259fwxr-byte.github.io/arrowgame/" target="_blank">Играть в Arrows Game</a></p>
            
            <h2>📝 Логи:</h2>
            <p>Последние действия можно посмотреть в логах PythonAnywhere.</p>
        </div>
    </body>
    </html>
    """

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Запуск Arrows Game Bot")
    print("=" * 50)
    print(f"📁 Файл данных: {DATA_FILE}")
    print(f"🤖 Токен бота: {BOT_TOKEN[:10]}...")
    print(f"📢 Канал: {CHANNEL_ID}")
    print(f"🎮 URL игры: {GAME_URL}")
    print("=" * 50)
    
    # Проверяем существование файла данных
    if os.path.exists(DATA_FILE):
        users = load_data()
        print(f"👥 Загружено {len(users)} пользователей")
    else:
        print("📝 Файл данных не найден, будет создан при первом запуске")
    
    # Запускаем Flask в режиме разработки
    app.run(debug=True, host='0.0.0.0', port=5000)
