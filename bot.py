import os
import json
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Конфигурация
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
DATA_FILE = "/home/malollas/arrows_data.json"
CHANNEL_ID = "@arrows_game"  # Канал для обязательной подписки
GAME_URL = "https://7fq259fwxr-byte.github.io/arrowgame/"
SUPPORT_BOT = "@arrow_game_supprot_bot"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_user_data(user_id, username):
    users = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {
            "username": username,
            "score": 0,
            "games_played": 0,
            "coins": 0,
            "level": 1,
            "last_active": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "first_seen": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    else:
        users[user_id_str]["last_active"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        users[user_id_str]["username"] = username
    
    save_data(users)
    return users[user_id_str]

def get_user_stats(user_id):
    users = load_data()
    user_id_str = str(user_id)
    
    if user_id_str in users:
        user_data = users[user_id_str]
        return {
            "username": user_data.get("username", "Гость"),
            "score": user_data.get("score", 0),
            "games_played": user_data.get("games_played", 0),
            "coins": user_data.get("coins", 0),
            "level": user_data.get("level", 1),
            "last_active": user_data.get("last_active", "Никогда")
        }
    return None

def get_leaderboard(limit=10):
    users = load_data()
    sorted_users = sorted(
        users.values(), 
        key=lambda x: x.get('score', 0), 
        reverse=True
    )[:limit]
    
    leaderboard = []
    for i, user in enumerate(sorted_users, 1):
        leaderboard.append({
            "rank": i,
            "username": user.get("username", "Гость"),
            "score": user.get("score", 0),
            "level": user.get("level", 1),
            "coins": user.get("coins", 0)
        })
    return leaderboard

def check_subscription_sync(user_id):
    """Синхронная проверка подписки через Telegram API"""
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
                # Статусы, которые считаются подпиской
                valid_statuses = ["creator", "administrator", "member"]
                return status in valid_statuses
        return False
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    """Отправка сообщения через Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return False

def edit_message_text(chat_id, message_id, text, reply_markup=None, parse_mode="Markdown"):
    """Редактирование сообщения через Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка редактирования сообщения: {e}")
        return False

# ==================== КЛАВИАТУРЫ ====================

def get_main_menu_keyboard():
    """Клавиатура главного меню"""
    return {
        "inline_keyboard": [
            [{"text": "🎮 Играть", "web_app": {"url": GAME_URL}}],
            [
                {"text": "📊 Статистика", "callback_data": "stats"},
                {"text": "🏆 Лидерборд", "callback_data": "leaderboard"}
            ],
            [
                {"text": "❓ Об игре", "callback_data": "about"},
                {"text": "🛠 Поддержка", "callback_data": "support"}
            ],
            [{"text": "💡 Предложить идею", "callback_data": "suggestion"}]
        ]
    }

def get_subscription_keyboard():
    """Клавиатура для подписки на канал"""
    return {
        "inline_keyboard": [
            [
                {"text": "📢 Подписаться на канал", "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"},
                {"text": "✅ Я подписался", "callback_data": "check_subscription"}
            ]
        ]
    }

def get_back_button():
    """Кнопка 'Назад'"""
    return {
        "inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]
    }

# ==================== ОБРАБОТЧИКИ КОМАНД ====================

def handle_start_command(chat_id, user_id, username, message_id=None):
    """Обработчик команды /start"""
    
    # Проверяем подписку
    if not check_subscription_sync(user_id):
        message_text = (
            "⚠️ *ДОСТУП ЗАКРЫТ*\n\n"
            "Для использования бота необходима подписка на наш канал!\n\n"
            "📢 *Arrows Game Channel*: @arrows_game\n\n"
            "1. Нажмите кнопку '📢 Подписаться на канал' ниже\n"
            "2. После вступления нажмите '✅ Я подписался'\n"
            "3. Если бот не видит подписку, подождите 10 секунд и попробуйте снова"
        )
        
        if message_id:
            return edit_message_text(chat_id, message_id, message_text, get_subscription_keyboard())
        else:
            return send_message(chat_id, message_text, get_subscription_keyboard())
    
    # Сохраняем пользователя
    save_user_data(user_id, username)
    
    # Отправляем главное меню
    message_text = (
        f"🎮 *Добро пожаловать в Arrows Pro Ultra, {username}!* 🎮\n\n"
        "*Доступ открыт!* ✅ Вы подписаны на канал @arrows_game\n\n"
        "*Выберите действие:*"
    )
    
    if message_id:
        return edit_message_text(chat_id, message_id, message_text, get_main_menu_keyboard())
    else:
        return send_message(chat_id, message_text, get_main_menu_keyboard())

def handle_stats(chat_id, user_id, message_id):
    """Обработчик статистики"""
    stats = get_user_stats(user_id)
    if stats:
        stats_text = (
            f"📊 *ВАША СТАТИСТИКА*\n\n"
            f"👤 *Игрок:* {stats['username']}\n"
            f"🏆 *Уровень:* {stats['level']}\n"
            f"⭐ *Очки:* {stats['score']}\n"
            f"💰 *Монеты:* {stats['coins']}\n"
            f"🎮 *Игр сыграно:* {stats['games_played']}\n"
            f"🕐 *Последняя активность:* {stats['last_active']}"
        )
    else:
        stats_text = "Вы еще не начали играть! Нажмите '🎮 Играть', чтобы начать."
    
    return edit_message_text(chat_id, message_id, stats_text, get_back_button())

def handle_leaderboard(chat_id, message_id):
    """Обработчик лидерборда"""
    leaderboard = get_leaderboard()
    
    leaderboard_text = "🏆 *ТОП-10 ИГРОКОВ*\n\n"
    for player in leaderboard:
        medal = ""
        if player['rank'] == 1:
            medal = "🥇"
        elif player['rank'] == 2:
            medal = "🥈"
        elif player['rank'] == 3:
            medal = "🥉"
        else:
            medal = f"{player['rank']}."
        
        leaderboard_text += f"{medal} *{player['username']}*\n   Уровень: {player['level']} | Очки: {player['score']} | Монеты: {player['coins']}\n\n"
    
    return edit_message_text(chat_id, message_id, leaderboard_text, get_back_button())

def handle_about(chat_id, message_id):
    """Обработчик 'Об игре'"""
    about_text = (
        "🎮 *ARROWS PRO ULTRA*\n\n"
        "*ОБ ИГРЕ:*\n"
        "Arrows Pro Ultra - увлекательная логическая игра, где нужно расставлять стрелки на поле так, чтобы они не сталкивались.\n\n"
        "*ОСНОВНЫЕ МЕХАНИКИ:*\n"
        "• 🎯 Расставляйте стрелки на игровом поле\n"
        "• 🚫 Избегайте столкновений стрелок\n"
        "• 📈 Проходите уровни и повышайте сложность\n"
        "• 💰 Зарабатывайте монеты за победы\n"
        "• 🏆 Соревнуйтесь с другими игроками\n\n"
        "*ОСОБЕННОСТИ:*\n"
        "✅ Простой и понятный геймплей\n"
        "✅ Постепенно возрастающая сложность\n"
        "✅ Система достижений и монет\n"
        "✅ Таблица лидеров\n"
        "✅ Регулярные обновления\n\n"
        "*ОБЯЗАТЕЛЬНО:* Подписка на канал @arrows_game\n\n"
        "Для начала игры нажмите '🎮 Играть' в главном меню!"
    )
    
    return edit_message_text(chat_id, message_id, about_text, get_back_button())

def handle_support(chat_id, message_id):
    """Обработчик поддержки"""
    support_text = (
        f"🛠 *ПОДДЕРЖКА*\n\n"
        f"*Если у вас возникли проблемы с игрой или есть вопросы:*\n\n"
        f"👨‍💻 *Техническая поддержка:* {SUPPORT_BOT}\n\n"
        f"*Мы поможем с:*\n"
        f"• 🐛 Техническими проблемами\n"
        f"• ❓ Вопросами по геймплею\n"
        f"• 🔧 Неполадками в игре\n"
        f"• 📱 Проблемами с запуском\n"
        f"• 📢 Вопросами по подписке на канал\n\n"
        f"*Время ответа:* обычно в течение 24 часов\n\n"
        f"*Не стесняйтесь обращаться, мы всегда рады помочь!* 😊"
    )
    
    return edit_message_text(chat_id, message_id, support_text, get_back_button())

def handle_suggestion(chat_id, message_id):
    """Обработчик предложений"""
    suggestion_text = (
        f"💡 *ПРЕДЛОЖИТЬ ИДЕЮ*\n\n"
        f"*У вас есть идея, как улучшить игру? Мы будем рады её услышать!*\n\n"
        f"📝 *Отправляйте свои предложения:* {SUPPORT_BOT}\n\n"
        f"*Что можно предложить:*\n"
        f"• 🎮 Новые механики геймплея\n"
        f"• 🎨 Улучшения интерфейса\n"
        f"• 📊 Дополнительные статистики\n"
        f"• 🏆 Новые достижения\n"
        f"• 🔧 Технические улучшения\n\n"
        f"*Наши критерии:*\n"
        f"✅ Идея должна быть оригинальной\n"
        f"✅ Предложение должно быть детальным\n"
        f"✅ Учитывайте баланс игры\n\n"
        f"*Лучшие идеи будут реализованы в следующих обновлениях!*"
    )
    
    return edit_message_text(chat_id, message_id, suggestion_text, get_back_button())

def handle_back_button(chat_id, user_id, message_id):
    """Обработчик кнопки 'Назад'"""
    user_data = get_user_stats(user_id)
    username = user_data["username"] if user_data else "Гость"
    
    message_text = (
        f"🎮 *Главное меню Arrows Pro Ultra* 🎮\n\n"
        f"*Игрок:* {username}\n"
        f"*Статус:* ✅ Подписка активна\n\n"
        f"*Выберите действие:*"
    )
    
    return edit_message_text(chat_id, message_id, message_text, get_main_menu_keyboard())

# ==================== ВЕБХУК ====================

@app.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    """Основной обработчик вебхука от Telegram"""
    update = request.get_json()
    
    # Логируем входящее обновление (для отладки)
    logger.info(f"Получено обновление: {update}")
    
    # Обработка сообщений
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        user_id = update["message"]["from"]["id"]
        username = update["message"]["from"].get("username", 
                    update["message"]["from"].get("first_name", "Гость"))
        
        # Проверяем наличие текста
        if "text" in update["message"]:
            text = update["message"]["text"]
            
            # Обработка команды /start
            if text.startswith("/start"):
                return handle_start_command(chat_id, user_id, username)
            
            # Обработка других команд
            elif text.startswith("/help"):
                help_text = (
                    f"📚 *ДОСТУПНЫЕ КОМАНДЫ*\n\n"
                    f"/start - Запустить бота и показать главное меню\n"
                    f"/help - Показать это сообщение помощи\n"
                    f"/stats - Показать вашу статистику\n"
                    f"/leaderboard - Показать таблицу лидеров\n\n"
                    f"*ОСНОВНЫЕ ФУНКЦИИ:*\n"
                    f"• 🎮 Играть - Запустить игру в мини-приложении\n"
                    f"• 📊 Статистика - Посмотреть вашу статистику\n"
                    f"• 🏆 Лидерборд - Таблица лучших игроков\n"
                    f"• ❓ Об игре - Информация об игре\n"
                    f"• 🛠 Поддержка - Связь с техподдержкой\n"
                    f"• 💡 Предложить идею - Отправить предложение по улучшению\n\n"
                    f"*ОБЯЗАТЕЛЬНО:* Подписка на канал @arrows_game\n\n"
                    f"*По всем вопросам:* {SUPPORT_BOT}"
                )
                send_message(chat_id, help_text)
                
            elif text.startswith("/stats"):
                # Сначала проверяем подписку
                if not check_subscription_sync(user_id):
                    send_message(chat_id, "❌ Для доступа к статистике нужна подписка на канал @arrows_game")
                    return jsonify({"status": "ok"}), 200
                
                # Показываем статистику
                message_text = "📊 *ВАША СТАТИСТИКА*\n\n"
                stats = get_user_stats(user_id)
                if stats:
                    message_text += (
                        f"👤 *Игрок:* {stats['username']}\n"
                        f"🏆 *Уровень:* {stats['level']}\n"
                        f"⭐ *Очки:* {stats['score']}\n"
                        f"💰 *Монеты:* {stats['coins']}\n"
                        f"🎮 *Игр сыграно:* {stats['games_played']}\n"
                        f"🕐 *Последняя активность:* {stats['last_active']}"
                    )
                else:
                    message_text = "Вы еще не начали играть! Нажмите '🎮 Играть', чтобы начать."
                
                send_message(chat_id, message_text)
                
            elif text.startswith("/leaderboard"):
                # Сначала проверяем подписку
                if not check_subscription_sync(user_id):
                    send_message(chat_id, "❌ Для доступа к лидерборду нужна подписка на канал @arrows_game")
                    return jsonify({"status": "ok"}), 200
                
                # Показываем лидерборд
                leaderboard = get_leaderboard()
                leaderboard_text = "🏆 *ТОП-10 ИГРОКОВ*\n\n"
                for player in leaderboard:
                    medal = ""
                    if player['rank'] == 1:
                        medal = "🥇"
                    elif player['rank'] == 2:
                        medal = "🥈"
                    elif player['rank'] == 3:
                        medal = "🥉"
                    else:
                        medal = f"{player['rank']}."
                    
                    leaderboard_text += f"{medal} *{player['username']}*\n   Уровень: {player['level']} | Очки: {player['score']} | Монеты: {player['coins']}\n\n"
                
                send_message(chat_id, leaderboard_text)
                
            else:
                # Прочие текстовые сообщения
                if not check_subscription_sync(user_id):
                    send_message(chat_id, "❌ Для использования бота нужна подписка на канал @arrows_game\n\nИспользуйте /start для начала работы")
                else:
                    send_message(chat_id, "🤔 Используйте /start для отображения меню или /help для помощи.")
    
    # Обработка callback-запросов (нажатия на кнопки)
    elif "callback_query" in update:
        callback_query = update["callback_query"]
        chat_id = callback_query["message"]["chat"]["id"]
        message_id = callback_query["message"]["message_id"]
        user_id = callback_query["from"]["id"]
        callback_data = callback_query["data"]
        
        # Отвечаем на callback (убираем часики)
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
            json={"callback_query_id": callback_query["id"]}
        )
        
        # Обработка разных callback_data
        if callback_data == "check_subscription":
            # Проверяем подписку
            if check_subscription_sync(user_id):
                username = callback_query["from"].get("username", 
                           callback_query["from"].get("first_name", "Гость"))
                save_user_data(user_id, username)
                handle_back_button(chat_id, user_id, message_id)
            else:
                edit_message_text(
                    chat_id, message_id,
                    "❌ *ПОДПИСКА НЕ ОБНАРУЖЕНА!*\n\n"
                    "*Убедитесь, что вы:*\n"
                    "1. Действительно вступили в канал: @arrows_game\n"
                    "2. Нажали кнопку '✅ Я подписался' после вступления\n"
                    "3. Если только что подписались, подождите 10 секунд\n\n"
                    "*Если проблема persists:*\n"
                    "• Проверьте, не вышел ли вы случайно из канала\n"
                    "• Убедитесь, что канал публичный\n"
                    "• Попробуйте начать снова с /start",
                    get_subscription_keyboard()
                )
        
        elif callback_data == "back":
            handle_back_button(chat_id, user_id, message_id)
        
        elif callback_data == "stats":
            # Проверяем подписку
            if not check_subscription_sync(user_id):
                edit_message_text(
                    chat_id, message_id,
                    "❌ *ДОСТУП ОТКЛЮЧЕН*\n\n"
                    "Ваша подписка на канал @arrows_game не активна!\n\n"
                    "Обновите подписку и нажмите кнопку ниже:",
                    get_subscription_keyboard()
                )
            else:
                handle_stats(chat_id, user_id, message_id)
        
        elif callback_data == "leaderboard":
            # Проверяем подписку
            if not check_subscription_sync(user_id):
                edit_message_text(
                    chat_id, message_id,
                    "❌ *ДОСТУП ОТКЛЮЧЕН*\n\n"
                    "Ваша подписка на канал @arrows_game не активна!\n\n"
                    "Обновите подписку и нажмите кнопку ниже:",
                    get_subscription_keyboard()
                )
            else:
                handle_leaderboard(chat_id, message_id)
        
        elif callback_data == "about":
            # Проверяем подписку
            if not check_subscription_sync(user_id):
                edit_message_text(
                    chat_id, message_id,
                    "❌ *ДОСТУП ОТКЛЮЧЕН*\n\n"
                    "Ваша подписка на канал @arrows_game не активна!\n\n"
                    "Обновите подписку и нажмите кнопку ниже:",
                    get_subscription_keyboard()
                )
            else:
                handle_about(chat_id, message_id)
        
        elif callback_data == "support":
            # Проверяем подписку
            if not check_subscription_sync(user_id):
                edit_message_text(
                    chat_id, message_id,
                    "❌ *ДОСТУП ОТКЛЮЧЕН*\n\n"
                    "Ваша подписка на канал @arrows_game не активна!\n\n"
                    "Обновите подписку и нажмите кнопку ниже:",
                    get_subscription_keyboard()
                )
            else:
                handle_support(chat_id, message_id)
        
        elif callback_data == "suggestion":
            # Проверяем подписку
            if not check_subscription_sync(user_id):
                edit_message_text(
                    chat_id, message_id,
                    "❌ *ДОСТУП ОТКЛЮЧЕН*\n\n"
                    "Ваша подписка на канал @arrows_game не активна!\n\n"
                    "Обновите подписку и нажмите кнопку ниже:",
                    get_subscription_keyboard()
                )
            else:
                handle_suggestion(chat_id, message_id)
    
    return jsonify({"status": "ok"}), 200

# ==================== СТАРЫЕ API ЭНДПОИНТЫ (для игры) ====================

@app.route('/api/get_user', methods=['POST'])
def get_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data received"}), 400

        user_id = str(data.get('user_id', 'unknown'))
        username = data.get('username', 'Guest')

        users = load_data()

        if user_id not in users:
            users[user_id] = {
                "username": username,
                "score": 0,
                "games_played": 0,
                "coins": 0,
                "level": 1,
                "last_active": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "first_seen": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            save_data(users)

        return jsonify({
            "success": True,
            "user": users[user_id]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        "success": True,
        "message": "API работает нормально!",
        "server_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard_api():
    users = load_data()
    sorted_users = sorted(users.values(), key=lambda x: x.get('score', 0), reverse=True)[:10]
    return jsonify(sorted_users)

# ==================== НАСТРОЙКА ВЕБХУКА ====================

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука для Telegram бота"""
    webhook_url = f"https://malollas.pythonanywhere.com/api/telegram"
    method = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    
    try:
        r = requests.get(method)
        result = r.json()
        
        if result.get("ok"):
            return jsonify({
                "success": True,
                "message": "Webhook успешно установлен!",
                "url": webhook_url
            })
        else:
            return jsonify({
                "success": False,
                "message": "Ошибка установки webhook",
                "error": result.get("description", "Unknown error")
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Ошибка установки webhook",
            "error": str(e)
        })

@app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    """Удаление вебхука"""
    method = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    
    try:
        r = requests.get(method)
        result = r.json()
        
        if result.get("ok"):
            return jsonify({
                "success": True,
                "message": "Webhook успешно удален!"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Ошибка удаления webhook",
                "error": result.get("description", "Unknown error")
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Ошибка удаления webhook",
            "error": str(e)
        })

@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    """Получение информации о текущем вебхуке"""
    method = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    
    try:
        r = requests.get(method)
        result = r.json()
        
        return jsonify({
            "success": result.get("ok", False),
            "webhook_info": result.get("result", {})
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
