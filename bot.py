import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Конфигурация
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
DATA_FILE = "/home/malollas/arrows_data.json"
CHANNEL_ID = "@arrows_game"
GAME_URL = "https://7fq259fwxr-byte.github.io/arrowgame/"
BANNER_URL = "https://github.com/7fq259fwxr-byte/arrowgame/blob/910f4b5f6e70976b166a005f73c3d69d405f786f/IMG_9228.png"  # Замени на реальный URL баннера

# Мультиязычные тексты
TEXTS = {
    "ru": {
        "welcome": """🎮 *ДОБРО ПОЖАЛОВАТЬ В ARROWS GAME, {username}!*

Arrows Pro — это захватывающая игра на логику, где твоя цель — очистить поле от всех стрелок!

🎯 *СУТЬ ИГРЫ:*
• На игровом поле расположены стрелки
• Каждая стрелка указывает направление (вверх, вниз, влево, вправо)
• Нажимай на стрелки, чтобы они "вылетали" с поля
• Стрелки, которые сталкиваются с другими, возвращаются назад
• *Цель: очистить всё поле, кликая по стрелкам в правильном порядке!*

✨ *ОСОБЕННОСТИ:*
• 🧠 Развивает логическое мышление
• 🎯 100+ уровней сложности
• 🏆 Система лидерборда
• 💰 Внутриигровая валюта
• 🎨 Скины для стрелок (coming soon)

*Выберите действие ниже:*""",
        "subscribe": "⚠️ *Для использования бота нужно подписаться на канал @arrows_game*\n\nПосле подписки нажмите кнопку 'Проверить'",
        "sub_confirmed": "✅ *Подписка подтверждена!*\n\nИспользуйте /start для доступа к меню.",
        "not_subscribed": "❌ *Вы еще не подписались!*\n\nНажмите кнопку ниже, чтобы подписаться на @arrows_game",
        "stats": """📊 *ВАША СТАТИСТИКА В ARROWS GAME:*

🎮 *Игрок:* {username}
🏆 *Текущий уровень:* {level}
⭐ *Пройдено уровней:* {score}
💰 *Монеты:* {coins}
🎯 *Игр сыграно:* {games_played}
🕒 *Последняя активность:* {last_active}

*Совет:* Чтобы пройти уровень, нужно очистить поле от всех стрелок, нажимая на них в правильном порядке!""",
        "top_empty": "🏆 *Топ игроков:*\n\nПока никто не играл. Будьте первым!",
        "top_header": "🏆 *Топ-10 игроков Arrows Game:*\n\n",
        "back_menu": "🎮 *Меню Arrows Game*\n\nПривет, {username}! Выберите действие:",
        "subscribe_btn": "📢 Подписаться",
        "check_btn": "✅ Проверить",
        "play_btn": "🎮 НАЧАТЬ ИГРУ",
        "stats_btn": "📊 Моя статистика",
        "top_btn": "🏆 Топ игроков",
        "support_btn": "🛠 Поддержка",
        "channel_btn": "📢 Наш канал",
        "continue_btn": "🎮 Продолжить игру",
        "back_btn": "🔙 Назад",
        "play_simple_btn": "🎮 Играть"
    },
    "en": {
        "welcome": """🎮 *WELCOME TO ARROWS GAME, {username}!*

Arrows Pro is an exciting logic game where your goal is to clear the field of all arrows!

🎯 *GAME ESSENCE:*
• Arrows are placed on the game field
• Each arrow points in a direction (up, down, left, right)
• Click arrows to make them "fly out" of the field
• Arrows that collide with others bounce back
• *Goal: Clear the entire field by clicking arrows in the correct order!*

✨ *FEATURES:*
• 🧠 Develops logical thinking
• 🎯 100+ difficulty levels
• 🏆 Leaderboard system
• 💰 In-game currency
• 🎨 Arrow skins (coming soon)

*Choose an action below:*""",
        "subscribe": "⚠️ *To use the bot you need to subscribe to the channel @arrows_game*\n\nAfter subscribing, click the 'Check' button",
        "sub_confirmed": "✅ *Subscription confirmed!*\n\nUse /start to access the menu.",
        "not_subscribed": "❌ *You haven't subscribed yet!*\n\nClick the button below to subscribe to @arrows_game",
        "stats": """📊 *YOUR STATISTICS IN ARROWS GAME:*

🎮 *Player:* {username}
🏆 *Current level:* {level}
⭐ *Levels completed:* {score}
💰 *Coins:* {coins}
🎯 *Games played:* {games_played}
🕒 *Last active:* {last_active}

*Tip:* To pass a level, you need to clear the field of all arrows by clicking them in the correct order!""",
        "top_empty": "🏆 *Top players:*\n\nNo one has played yet. Be the first!",
        "top_header": "🏆 *Top-10 Arrows Game Players:*\n\n",
        "back_menu": "🎮 *Arrows Game Menu*\n\nHello, {username}! Choose an action:",
        "subscribe_btn": "📢 Subscribe",
        "check_btn": "✅ Check",
        "play_btn": "🎮 START GAME",
        "stats_btn": "📊 My Statistics",
        "top_btn": "🏆 Top Players",
        "support_btn": "🛠 Support",
        "channel_btn": "📢 Our Channel",
        "continue_btn": "🎮 Continue Game",
        "back_btn": "🔙 Back",
        "play_simple_btn": "🎮 Play"
    },
    "zh": {
        "welcome": """🎮 *欢迎来到ARROWS GAME, {username}!*

Arrows Pro 是一款令人兴奋的逻辑游戏，你的目标是清除场上所有箭头！

🎯 *游戏本质：*
• 箭头放置在游戏场上
• 每个箭头指向一个方向（上、下、左、右）
• 点击箭头让它们"飞出"场地
• 与其他箭头碰撞的箭头会反弹回来
• *目标：通过按正确顺序点击箭头来清除整个场地！*

✨ *特点：*
• 🧠 培养逻辑思维
• 🎯 100+难度等级
• 🏆 排行榜系统
• 💰 游戏内货币
• 🎨 箭头皮肤 (即将推出)

*选择以下操作：*""",
        "subscribe": "⚠️ *要使用机器人，您需要订阅频道 @arrows_game*\n\n订阅后，点击'检查'按钮",
        "sub_confirmed": "✅ *订阅确认！*\n\n使用 /start 访问菜单。",
        "not_subscribed": "❌ *您尚未订阅！*\n\n点击下方按钮订阅 @arrows_game",
        "stats": """📊 *您在ARROWS GAME中的统计数据：*

🎮 *玩家：* {username}
🏆 *当前等级：* {level}
⭐ *完成等级：* {score}
💰 *金币：* {coins}
🎯 *游戏次数：* {games_played}
🕒 *最后活跃：* {last_active}

*提示：* 要通过关卡，您需要通过按正确顺序点击所有箭头来清除场地！""",
        "top_empty": "🏆 *顶级玩家：*\n\n还没有人玩过。成为第一个！",
        "top_header": "🏆 *Arrows Game前10名玩家：*\n\n",
        "back_menu": "🎮 *Arrows Game菜单*\n\n你好, {username}! 选择操作：",
        "subscribe_btn": "📢 订阅",
        "check_btn": "✅ 检查",
        "play_btn": "🎮 开始游戏",
        "stats_btn": "📊 我的统计",
        "top_btn": "🏆 顶级玩家",
        "support_btn": "🛠 支持",
        "channel_btn": "📢 我们的频道",
        "continue_btn": "🎮 继续游戏",
        "back_btn": "🔙 返回",
        "play_simple_btn": "🎮 游戏"
    }
}

def get_user_language(user_id, from_tg=None):
    """Определяем язык пользователя"""
    try:
        # Пока используем русский по умолчанию
        # В будущем можно сохранять язык в данных пользователя
        return "ru"
    except:
        return "ru"

def send_welcome_with_photo(chat_id, username, lang):
    """Отправляет приветственное сообщение с фото"""
    try:
        welcome_text = TEXTS[lang]["welcome"].format(username=username)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": TEXTS[lang]["play_btn"], "web_app": {"url": GAME_URL}}],
                [
                    {"text": TEXTS[lang]["stats_btn"], "callback_data": "stats"},
                    {"text": TEXTS[lang]["top_btn"], "callback_data": "top"}
                ],
                [
                    {"text": TEXTS[lang]["support_btn"], "url": "https://t.me/arrow_game_supprot_bot"},
                    {"text": TEXTS[lang]["channel_btn"], "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"}
                ]
            ]
        }
        
        # Сначала отправляем фото с текстом
        photo_response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            json={
                "chat_id": chat_id,
                "photo": BANNER_URL,
                "caption": f"🎮 *ДОБРО ПОЖАЛОВАТЬ В ARROWS GAME, {username}!*\n\nArrows Pro — это захватывающая игра на логику, где твоя цель — очистить поле от всех стрелок!",
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        
        # Затем отправляем подробное сообщение с кнопками
        if photo_response.status_code == 200:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": welcome_text,
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                },
                timeout=10
            )
        else:
            # Если не удалось отправить фото, отправляем только текст с кнопками
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": welcome_text,
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                },
                timeout=10
            )
            
        return True
    except Exception as e:
        print(f"Ошибка отправки приветствия с фото: {e}")
        return False

# ========== БАЗОВЫЕ ФУНКЦИИ ==========
def load_data():
    """Загружает данные из файла и нормализует структуру"""
    try:
        print(f"Загрузка данных из {DATA_FILE}")
        
        if not os.path.exists(DATA_FILE):
            print("Файл не существует, создаю пустую структуру")
            return {"users": {}, "shop_items": {}, "leaderboard": []}
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Загружено {len(data.get('users', {}))} пользователей из файла")
            
            # Если файл имеет старую структуру (пользователи в корне), конвертируем её
            if "users" not in data:
                print("Обнаружена старая структура файла, конвертирую...")
                users = {}
                for key, value in data.items():
                    if key.isdigit():  # Это user_id
                        users[key] = value
                
                # Сохраняем shop_items если есть
                shop_items = data.get("shop_items", {
                    "arrow_skins": [
                        {"id": "default", "name": "Классический", "price": 0},
                        {"id": "fire", "name": "Огненный", "price": 100},
                        {"id": "ice", "name": "Ледяной", "price": 150},
                        {"id": "gold", "name": "Золотой", "price": 300},
                        {"id": "neon", "name": "Неоновый", "price": 200},
                        {"id": "rainbow", "name": "Радужный", "price": 500}
                    ]
                })
                
                leaderboard = data.get("leaderboard", [])
                
                data = {
                    "users": users,
                    "shop_items": shop_items,
                    "leaderboard": leaderboard
                }
                
                # Сохраняем новую структуру
                save_normalized_data(data)
            
            return data
            
    except json.JSONDecodeError as e:
        print(f"Ошибка JSON: {e}")
        print("Создаю новую структуру данных...")
        return {"users": {}, "shop_items": {}, "leaderboard": []}
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        traceback.print_exc()
        return {"users": {}, "shop_items": {}, "leaderboard": []}

def save_normalized_data(data):
    """Сохраняет данные в нормализованной структуре"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(data.get('users', {}))} пользователей")
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

def get_users():
    """Получает словарь пользователей из данных"""
    data = load_data()
    return data.get("users", {})

def save_user(user_id, user_data):
    """Сохраняет данные одного пользователя"""
    try:
        data = load_data()
        users = data.get("users", {})
        
        # Обновляем данные пользователя
        user_id_str = str(user_id)
        if user_id_str not in users:
            users[user_id_str] = {}
        
        # Объединяем старые и новые данные
        users[user_id_str].update(user_data)
        
        # Добавляем/обновляем timestamp
        users[user_id_str]["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Сохраняем обратно
        data["users"] = users
        save_normalized_data(data)
        
        print(f"Сохранен пользователь {user_id_str}: {users[user_id_str]}")
        return True
    except Exception as e:
        print(f"Ошибка сохранения пользователя: {e}")
        return False

def update_user_score(user_id, username, level, coins_earned):
    """Обновляет счет пользователя"""
    try:
        user_id_str = str(user_id)
        users = get_users()
        
        if user_id_str not in users:
            # Создаем нового пользователя
            user_data = {
                "username": username,
                "score": level - 1,
                "games_played": 1,
                "level": level,
                "coins": coins_earned,
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            # Обновляем существующего
            user_data = users[user_id_str]
            
            # Увеличиваем счетчик игр
            user_data["games_played"] = user_data.get("games_played", 0) + 1
            
            # Обновляем уровень если он выше
            current_level = user_data.get("level", 1)
            if level > current_level:
                user_data["level"] = level
                user_data["score"] = level - 1
            
            # Добавляем монеты
            user_data["coins"] = user_data.get("coins", 0) + coins_earned
            
            # Обновляем имя если нужно
            if username and username != 'Guest':
                user_data["username"] = username
        
        save_user(user_id, user_data)
        return user_data
    except Exception as e:
        print(f"Ошибка обновления счета: {e}")
        return None

# ========== API ДЛЯ ИГРЫ ==========
@app.route('/api/get_user', methods=['POST'])
def get_user():
    """Получение данных пользователя для игры"""
    print("\n=== API: GET_USER ===")
    try:
        data = request.get_json()
        user_id = str(data.get('user_id', '0'))
        username = data.get('username', 'Guest')
        first_name = data.get('first_name', '')
        
        print(f"Запрос данных пользователя {user_id} ({username})")
        
        users = get_users()
        
        if user_id not in users:
            # Создаем нового пользователя
            user_data = {
                "username": username or f"User_{user_id}",
                "score": 0,
                "games_played": 0,
                "coins": 0,
                "level": 1,
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_user(user_id, user_data)
            print(f"Создан новый пользователь: {user_id}")
        else:
            user_data = users[user_id]
            print(f"Найден существующий пользователь: {user_data}")
        
        # Гарантируем наличие всех полей
        required_fields = ['username', 'score', 'games_played', 'coins', 'level']
        for field in required_fields:
            if field not in user_data:
                user_data[field] = 0 if field in ['score', 'games_played', 'coins'] else 1 if field == 'level' else ''
        
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
        user_id = str(data.get('user_id', '0'))
        username = data.get('username', 'Guest')
        level = int(data.get('level', 1))
        coins_earned = int(data.get('coins_earned', 0))
        
        print(f"Обновление счета для {user_id}: уровень={level}, монеты={coins_earned}")
        
        # Обновляем данные пользователя
        user_data = update_user_score(user_id, username, level, coins_earned)
        
        if user_data:
            return jsonify({
                "success": True, 
                "coins": user_data.get("coins", 0),
                "level": user_data.get("level", 1),
                "score": user_data.get("score", 0)
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update user score"
            }), 500
            
    except Exception as e:
        print(f"Ошибка в update_score: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получение таблицы лидеров для игры"""
    print("\n=== API: LEADERBOARD ===")
    try:
        users = get_users()
        print(f"Всего пользователей: {len(users)}")
        
        # Преобразуем в список для сортировки
        leaderboard_list = []
        for user_id_str, user_data in users.items():
            try:
                user_id_num = int(user_id_str)
            except:
                user_id_num = 0
            
            # Гарантируем наличие всех необходимых полей
            username = user_data.get("username", f"Player_{user_id_str}")
            score = user_data.get("score", 0)
            level = user_data.get("level", 1)
            coins = user_data.get("coins", 0)
            
            leaderboard_list.append({
                "user_id": user_id_num,
                "username": username,
                "score": score,
                "level": level,
                "coins": coins
            })
        
        # СОРТИРУЕМ ПО LEVEL, ПОТОМ ПО SCORE
        sorted_leaderboard = sorted(
            leaderboard_list,
            key=lambda x: (x.get('level', 1), x.get('score', 0)),
            reverse=True
        )[:100]  # Топ-100 для игры
        
        print(f"Лидерборд содержит {len(sorted_leaderboard)} игроков")
        
        # Если нет игроков, возвращаем пустой массив
        if not sorted_leaderboard:
            print("Лидерборд пуст")
        
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

@app.route('/api/get_user_rank', methods=['POST'])
def get_user_rank():
    """Получение глобального ранга пользователя"""
    print("\n=== API: GET_USER_RANK ===")
    try:
        data = request.get_json()
        user_id = str(data.get('user_id', '0'))
        
        print(f"Получение ранга для пользователя {user_id}")
        
        users = get_users()
        
        if not users or user_id not in users:
            return jsonify({
                "success": True,
                "rank": -1,  # Не в рейтинге
                "total_players": len(users)
            })
        
        # Создаем список всех пользователей для сортировки
        all_players = []
        for uid, user_data in users.items():
            all_players.append({
                "user_id": uid,
                "level": user_data.get("level", 1),
                "score": user_data.get("score", 0),
                "coins": user_data.get("coins", 0)
            })
        
        # Сортируем по уровню и очкам
        sorted_players = sorted(
            all_players,
            key=lambda x: (x.get('level', 1), x.get('score', 0)),
            reverse=True
        )
        
        # Находим позицию пользователя
        rank = -1
        for i, player in enumerate(sorted_players):
            if player['user_id'] == user_id:
                rank = i + 1  # +1 потому что рейтинг начинается с 1
                break
        
        return jsonify({
            "success": True,
            "rank": rank,
            "total_players": len(users),
            "level": users[user_id].get("level", 1),
            "score": users[user_id].get("score", 0),
            "coins": users[user_id].get("coins", 0)
        })
        
    except Exception as e:
        print(f"Ошибка в get_user_rank: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@app.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    """Вебхук для Telegram бота"""
    print("\n=== TELEGRAM WEBHOOK ===")
    try:
        update = request.get_json()
        
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_id = update["message"]["from"]["id"]
            username = update["message"]["from"].get("username", "Гость")
            text = update["message"]["text"]
            
            # Определяем язык пользователя
            lang = get_user_language(user_id, update["message"]["from"])
            
            if text == "/start" or text.startswith("/start"):
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
                except Exception as e:
                    print(f"Ошибка проверки подписки: {e}")
                    is_member = False
                
                if not is_member:
                    # Не подписан - просим подписаться
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": TEXTS[lang]["subscribe_btn"], "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"},
                            {"text": TEXTS[lang]["check_btn"], "callback_data": "check_sub"}
                        ]]
                    }
                    
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": TEXTS[lang]["subscribe"],
                            "parse_mode": "Markdown",
                            "reply_markup": keyboard
                        },
                        timeout=5
                    )
                else:
                    # Подписан - показываем меню
                    # Сохраняем пользователя
                    user_id_str = str(user_id)
                    users = get_users()
                    
                    if user_id_str not in users:
                        user_data = {
                            "username": username,
                            "score": 0,
                            "games_played": 0,
                            "coins": 0,
                            "level": 1,
                            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        save_user(user_id, user_data)
                    
                    # Отправляем приветствие с фото
                    send_welcome_with_photo(chat_id, username, lang)
        
        elif "callback_query" in update:
            callback = update["callback_query"]
            callback_id = callback["id"]
            chat_id = callback["message"]["chat"]["id"]
            message_id = callback["message"]["message_id"]
            user_id = callback["from"]["id"]
            data = callback["data"]
            
            print(f"Callback: {data} от {user_id}")
            
            # Определяем язык пользователя
            lang = get_user_language(user_id, callback["from"])
            
            # Отвечаем на callback (убираем "часики")
            try:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                    json={"callback_query_id": callback_id},
                    timeout=5
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
                            "text": TEXTS[lang]["sub_confirmed"],
                            "parse_mode": "Markdown"
                        },
                        timeout=5
                    )
                else:
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": TEXTS[lang]["subscribe_btn"], "url": f"https://t.me/{CHANNEL_ID.lstrip('@')}"},
                            {"text": TEXTS[lang]["check_btn"], "callback_data": "check_sub"}
                        ]]
                    }
                    
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                        json={
                            "chat_id": chat_id,
                            "message_id": message_id,
                            "text": TEXTS[lang]["not_subscribed"],
                            "parse_mode": "Markdown",
                            "reply_markup": keyboard
                        },
                        timeout=5
                    )
            
            elif data == "stats":
                users = get_users()
                user_key = str(user_id)
                user = users.get(user_key, {})
                
                stats_text = TEXTS[lang]["stats"].format(
                    username=user.get('username', 'Гость'),
                    level=user.get('level', 1),
                    score=user.get('score', 0),
                    coins=user.get('coins', 0),
                    games_played=user.get('games_played', 0),
                    last_active=user.get('last_active', 'никогда')
                )
                
                keyboard = {
                    "inline_keyboard": [[
                        {"text": TEXTS[lang]["continue_btn"], "web_app": {"url": GAME_URL}},
                        {"text": TEXTS[lang]["back_btn"], "callback_data": "back"}
                    ]]
                }
                
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": stats_text,
                        "parse_mode": "Markdown",
                        "reply_markup": keyboard
                    },
                    timeout=5
                )
            
            elif data == "top":
                try:
                    users = get_users()
                    print(f"Пользователей для лидерборда: {len(users)}")
                    
                    if not users:
                        top_text = TEXTS[lang]["top_empty"]
                    else:
                        # СОРТИРУЕМ ПО УРОВНЮ
                        sorted_users = sorted(
                            [(uid, data) for uid, data in users.items()],
                            key=lambda x: (x[1].get('level', 1), x[1].get('score', 0)),
                            reverse=True
                        )[:10]
                        
                        top_text = TEXTS[lang]["top_header"]
                        for i, (player_id, player_data) in enumerate(sorted_users, 1):
                            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                            name = player_data.get('username', f'Игрок_{player_id}')
                            if len(name) > 15:
                                name = name[:15] + "..."
                            level = player_data.get('level', 1)
                            top_text += f"{medal} *{name}*\n   🎯 Уровень: {level}\n\n"
                    
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": TEXTS[lang]["play_simple_btn"], "web_app": {"url": GAME_URL}},
                            {"text": TEXTS[lang]["back_btn"], "callback_data": "back"}
                        ]]
                    }
                    
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                        json={
                            "chat_id": chat_id,
                            "message_id": message_id,
                            "text": top_text,
                            "parse_mode": "Markdown",
                            "reply_markup": keyboard
                        },
                        timeout=5
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
                                "inline_keyboard": [[{"text": TEXTS[lang]["back_btn"], "callback_data": "back"}]]
                            }
                        },
                        timeout=5
                    )
            
            elif data == "back":
                username = callback["from"].get("username", "Гость")
                
                keyboard = {
                    "inline_keyboard": [
                        [{"text": TEXTS[lang]["play_simple_btn"], "web_app": {"url": GAME_URL}}],
                        [
                            {"text": TEXTS[lang]["stats_btn"], "callback_data": "stats"},
                            {"text": TEXTS[lang]["top_btn"], "callback_data": "top"}
                        ],
                        [
                            {"text": TEXTS[lang]["support_btn"], "url": "https://t.me/arrow_game_supprot_bot"}
                        ]
                    ]
                }
                
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": TEXTS[lang]["back_menu"].format(username=username),
                        "parse_mode": "Markdown",
                        "reply_markup": keyboard
                    },
                    timeout=5
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
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Отладочная информация"""
    try:
        data = load_data()
        users = data.get("users", {})
        
        info = {
            "success": True,
            "data_file": DATA_FILE,
            "file_exists": os.path.exists(DATA_FILE),
            "users_count": len(users),
            "users": users,
            "shop_items_exists": "shop_items" in data,
            "leaderboard_exists": "leaderboard" in data
        }
        
        return jsonify(info)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/fix_structure', methods=['GET'])
def fix_structure():
    """Исправляет структуру файла данных"""
    try:
        print("Исправление структуры файла данных...")
        
        # Загружаем текущие данные
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        # Создаем новую структуру
        new_data = {
            "users": {},
            "shop_items": old_data.get("shop_items", {}),
            "leaderboard": old_data.get("leaderboard", [])
        }
        
        # Переносим пользователей
        for key, value in old_data.items():
            if key.isdigit():  # Это user_id
                new_data["users"][key] = value
        
        # Сохраняем новую структуру
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        print(f"Структура исправлена. Перенесено {len(new_data['users'])} пользователей.")
        
        return jsonify({
            "success": True,
            "message": f"Структура исправлена. Перенесено {len(new_data['users'])} пользователей.",
            "users_count": len(new_data["users"])
        })
        
    except Exception as e:
        print(f"Ошибка исправления структуры: {e}")
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
        response = requests.get(url, timeout=10)
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
            <a href="/api/fix_structure" class="btn btn-danger">Исправить структуру данных</a>
            
            <h2>📊 API Endpoints:</h2>
            <div class="endpoint">GET /api/test - Тест работы API</div>
            <div class="endpoint">POST /api/get_user - Получить данные пользователя</div>
            <div class="endpoint">POST /api/update_score - Обновить счет</div>
            <div class="endpoint">GET /api/leaderboard - Получить лидерборд</div>
            <div class="endpoint">POST /api/get_user_rank - Получить глобальный ранг пользователя</div>
            <div class="endpoint">POST /api/telegram - Вебхук Telegram</div>
            <div class="endpoint">GET /api/debug - Отладочная информация</div>
            
            <h2>📝 Статус данных:</h2>
            <p id="status">Загрузка...</p>
            
            <script>
                fetch('/api/debug')
                    .then(response => response.json())
                    .then(data => {
                        if(data.success) {
                            document.getElementById('status').innerHTML = 
                                '✅ Файл данных: ' + data.data_file + '<br>' +
                                '👥 Пользователей: ' + data.users_count + '<br>' +
                                '🛍️ Магазин: ' + (data.shop_items_exists ? '✅' : '❌') + '<br>' +
                                '🏆 Лидерборд: ' + (data.leaderboard_exists ? '✅' : '❌');
                        } else {
                            document.getElementById('status').innerHTML = '❌ Ошибка: ' + data.error;
                        }
                    })
                    .catch(error => {
                        document.getElementById('status').innerHTML = '❌ Ошибка запроса: ' + error;
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
    
    # Проверяем файл данных
    if os.path.exists(DATA_FILE):
        print(f"📁 Файл данных найден: {DATA_FILE}")
        data = load_data()
        users = data.get("users", {})
        print(f"👥 Пользователей в базе: {len(users)}")
        
        # Показываем пользователей
        for user_id, user_data in users.items():
            print(f"   {user_id}: {user_data.get('username', 'Unknown')} - уровень {user_data.get('level', 1)}, очков: {user_data.get('score', 0)}")
    else:
        print(f"📁 Файл данных не найден. Будет создан при первом обращении.")
    
    print("=" * 60)
    print("🌐 Сервер запущен")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5000)
