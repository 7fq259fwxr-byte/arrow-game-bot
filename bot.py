#!/usr/bin/env python3
import requests
import json
import time
import logging
from flask import Flask, request, jsonify
import threading
import os

app = Flask(__name__)

# Конфигурация
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
GAME_URL = "https://ваш-сайт.github.io/arrows-game/"  # Замените на ваш

# База данных
DATA_FILE = "users_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "leaderboard": [], "shop_items": initialize_shop()}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def initialize_shop():
    return {
        "arrow_skins": [
            {"id": "default", "name": "Classic", "price": 0},
            {"id": "fire", "name": "Fire", "price": 100},
            {"id": "ice", "name": "Ice", "price": 150},
            {"id": "gold", "name": "Golden", "price": 300},
            {"id": "neon", "name": "Neon", "price": 200},
            {"id": "rainbow", "name": "Rainbow", "price": 500}
        ],
        "board_themes": [
            {"id": "default", "name": "Classic", "price": 0},
            {"id": "wood", "name": "Wood", "price": 200},
            {"id": "space", "name": "Space", "price": 300},
            {"id": "marble", "name": "Marble", "price": 250},
            {"id": "night", "name": "Night", "price": 180},
            {"id": "ocean", "name": "Ocean", "price": 220}
        ],
        "effects": [
            {"id": "none", "name": "No Effects", "price": 0},
            {"id": "sparkles", "name": "Sparkles", "price": 150},
            {"id": "confetti", "name": "Confetti", "price": 200},
            {"id": "fireworks", "name": "Fireworks", "price": 300},
            {"id": "glow", "name": "Glow", "price": 100},
            {"id": "trail", "name": "Trail", "price": 120}
        ]
    }

# API для игры
@app.route('/api/get_user_data', methods=['POST'])
def get_user_data():
    """Получение данных пользователя для игры"""
    data = request.json
    user_id = data.get('user_id')
    
    db = load_data()
    
    if str(user_id) in db["users"]:
        user_data = db["users"][str(user_id)]
        return jsonify({
            "success": True,
            "coins": user_data.get("coins", 0),
            "max_level": user_data.get("max_level", 1),
            "username": user_data.get("username", "Player"),
            "skins": user_data.get("skins", ["default"]),
            "selected_skin": user_data.get("selected_skin", "default"),
            "shop_items": db["shop_items"]
        })
    
    return jsonify({"success": False, "error": "User not found"})

@app.route('/api/update_score', methods=['POST'])
def update_score():
    """Обновление счета пользователя"""
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    new_level = data.get('level')
    coins_earned = data.get('coins_earned', 0)
    
    db = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in db["users"]:
        db["users"][user_id_str] = {
            "username": username,
            "coins": 0,
            "max_level": 1,
            "skins": ["default"],
            "selected_skin": "default",
            "purchases": [],
            "created_at": time.time()
        }
    
    user = db["users"][user_id_str]
    user["coins"] = user.get("coins", 0) + coins_earned
    
    if new_level > user.get("max_level", 1):
        user["max_level"] = new_level
    
    # Обновляем лидерборд
    update_leaderboard(db, user_id_str, username, user["max_level"])
    
    save_data(db)
    
    return jsonify({"success": True, "coins": user["coins"]})

@app.route('/api/purchase_item', methods=['POST'])
def purchase_item():
    """Покупка предмета в магазине"""
    data = request.json
    user_id = data.get('user_id')
    item_id = data.get('item_id')
    item_type = data.get('item_type')  # arrow, board, effect
    
    db = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in db["users"]:
        return jsonify({"success": False, "error": "User not found"})
    
    user = db["users"][user_id_str]
    
    # Находим предмет в магазине
    shop_items = db["shop_items"]
    item = None
    if item_type == "arrow":
        item = next((i for i in shop_items["arrow_skins"] if i["id"] == item_id), None)
    elif item_type == "board":
        item = next((i for i in shop_items["board_themes"] if i["id"] == item_id), None)
    elif item_type == "effect":
        item = next((i for i in shop_items["effects"] if i["id"] == item_id), None)
    
    if not item:
        return jsonify({"success": False, "error": "Item not found"})
    
    # Проверяем, не куплен ли уже предмет
    if item_id in user.get("skins", []):
        return jsonify({"success": False, "error": "Already purchased"})
    
    # Проверяем достаточно ли монет
    if user["coins"] < item["price"]:
        return jsonify({"success": False, "error": "Not enough coins"})
    
    # Совершаем покупку
    user["coins"] -= item["price"]
    if "skins" not in user:
        user["skins"] = []
    user["skins"].append(item_id)
    
    if "purchases" not in user:
        user["purchases"] = []
    user["purchases"].append({
        "item_id": item_id,
        "item_type": item_type,
        "price": item["price"],
        "timestamp": time.time()
    })
    
    save_data(db)
    
    return jsonify({
        "success": True, 
        "coins": user["coins"],
        "skins": user["skins"]
    })

@app.route('/api/select_item', methods=['POST'])
def select_item():
    """Выбор активного предмета"""
    data = request.json
    user_id = data.get('user_id')
    item_id = data.get('item_id')
    item_type = data.get('item_type')
    
    db = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in db["users"]:
        return jsonify({"success": False, "error": "User not found"})
    
    user = db["users"][user_id_str]
    
    # Проверяем, есть ли предмет у пользователя
    if item_id not in user.get("skins", []):
        return jsonify({"success": False, "error": "Item not owned"})
    
    # Выбираем предмет
    if item_type == "arrow":
        user["selected_skin"] = item_id
    # Для других типов можно добавить аналогично
    
    save_data(db)
    
    return jsonify({"success": True})

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получение таблицы лидеров"""
    db = load_data()
    
    # Создаем список для лидерборда
    leaderboard = []
    for user_id, user_data in db["users"].items():
        leaderboard.append({
            "user_id": user_id,
            "username": user_data["username"],
            "score": user_data["max_level"],
            "coins": user_data["coins"]
        })
    
    # Сортируем по уровню
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    return jsonify({"success": True, "leaderboard": leaderboard[:20]})

def update_leaderboard(db, user_id, username, score):
    """Обновление лидерборда"""
    # Ищем пользователя в лидерборде
    found = False
    for entry in db["leaderboard"]:
        if entry["user_id"] == user_id:
            if score > entry["score"]:
                entry["score"] = score
                entry["username"] = username
                entry["updated_at"] = time.time()
            found = True
            break
    
    if not found:
        db["leaderboard"].append({
            "user_id": user_id,
            "username": username,
            "score": score,
            "updated_at": time.time()
        })
    
    # Сортируем лидерборд
    db["leaderboard"].sort(key=lambda x: x["score"], reverse=True)
    # Оставляем только топ-50
    db["leaderboard"] = db["leaderboard"][:50]

# Telegram бот
def send_telegram_message(chat_id, text, keyboard=None):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    if keyboard:
        payload["reply_markup"] = keyboard
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return None

def get_user_stats(user_id):
    """Получение статистики пользователя"""
    db = load_data()
    user_id_str = str(user_id)
    
    if user_id_str in db["users"]:
        user = db["users"][user_id_str]
        
        # Определяем позицию в лидерборде
        position = 1
        for entry in db["leaderboard"]:
            if entry["user_id"] == user_id_str:
                break
            position += 1
        
        return f"""
📊 *ВАША СТАТИСТИКА:*

🏆 *Уровень:* {user['max_level']}
💰 *Монеты:* {user['coins']} 🪙
🥇 *Место в рейтинге:* #{position}
🎨 *Скинов:* {len(user.get('skins', ['default']))}

*Продолжайте в том же духе!* 🚀
        """
    
    return "Вы еще не играли. Начните сейчас! 🎮"

def handle_telegram_update(update):
    """Обработка обновлений Telegram"""
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user = message["from"]
        
        # Сохраняем пользователя
        db = load_data()
        user_id_str = str(user["id"])
        
        if user_id_str not in db["users"]:
            username = user.get("username", f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            if not username:
                username = f"Player{user_id_str[-4:]}"
            db["users"][user_id_str] = {
                "username": username,
                "coins": 0,
                "max_level": 1,
                "skins": ["default"],
                "selected_skin": "default",
                "created_at": time.time()
            }
            save_data(db)
        
        if text == "/start":
            keyboard = {
                "inline_keyboard": [[
                    {"text": "🎮 НАЧАТЬ ИГРУ", "web_app": {"url": GAME_URL}}
                ]]
            }
            
            welcome_text = f"""
Привет, {user.get('first_name', 'Игрок')}! 👋

🎮 *Arrows Pro Ultra* - новая версия с:
• Системой монет и наград
• Реальной таблицей лидеров
• Магазином скинов
• Прогрессом между уровнями

*Начните играть и зарабатывайте монеты!* 🪙

🏆 *Ваш прогресс сохраняется автоматически*
            """
            
            send_telegram_message(chat_id, welcome_text, keyboard)
        
        elif text == "/stats":
            stats_text = get_user_stats(user["id"])
            keyboard = {
                "inline_keyboard": [[
                    {"text": "🎮 ПРОДОЛЖИТЬ ИГРУ", "web_app": {"url": GAME_URL}}
                ]]
            }
            send_telegram_message(chat_id, stats_text, keyboard)
        
        elif text == "/leaderboard":
            db = load_data()
            
            if not db["leaderboard"]:
                send_telegram_message(chat_id, "Таблица лидеров пока пуста. Будьте первым! 🏆")
                return
            
            leader_text = "🏆 *ТОП-10 ИГРОКОВ:*\n\n"
            for i, entry in enumerate(db["leaderboard"][:10], 1):
                leader_text += f"{i}. {entry['username']} - Уровень {entry['score']}\n"
            
            # Получаем позицию пользователя
            position = 1
            user_found = False
            for entry in db["leaderboard"]:
                if entry["user_id"] == user_id_str:
                    user_found = True
                    break
                position += 1
            
            if user_found:
                leader_text += f"\nВаше место: #{position}"
            else:
                leader_text += f"\nВаше место: >10"
            
            keyboard = {
                "inline_keyboard": [[
                    {"text": "🎮 ИГРАТЬ", "web_app": {"url": GAME_URL}}
                ]]
            }
            
            send_telegram_message(chat_id, leader_text, keyboard)

def telegram_polling():
    """Поллинг Telegram бота"""
    offset = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("result"):
                    for update in data["result"]:
                        offset = update["update_id"] + 1
                        handle_telegram_update(update)
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Ошибка polling: {e}")
            time.sleep(5)

# Запуск Flask и Telegram бота
def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == "__main__":
    print("="*60)
    print("🤖 ARROWS PRO ULTRA - БОТ СО СТАТИСТИКОЙ")
    print("="*60)
    print("🎮 Игра: ", GAME_URL)
    print("📊 API: http://localhost:8080/api/")
    print("="*60)
    
    # Создаем файл данных если его нет
    if not os.path.exists(DATA_FILE):
        save_data({"users": {}, "leaderboard": [], "shop_items": initialize_shop()})
        print("✅ Создан файл данных с магазином")
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Даем Flask время на запуск
    time.sleep(2)
    
    # Запускаем Telegram бота
    print("🚀 Запуск Telegram бота...")
    telegram_polling()
