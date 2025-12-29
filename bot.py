#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arrows Pro Ultra Bot с авто-пингом для Replit
"""

import threading
import requests
import time
from flask import Flask
import logging

# ====================== КОНФИГУРАЦИЯ ======================
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
GAME_URL = "https://7fq259fwxr-byte.github.io/arrows-game/"
SUPPORT_BOT = "@arrow_game_support_bot"

# ====================== FLASK ДЛЯ ПИНГОВ ======================
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arrows Pro Ultra Bot</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .status { color: green; font-size: 24px; }
        </style>
    </head>
    <body>
        <h1>🤖 Arrows Pro Ultra Bot</h1>
        <div class="status">✅ Bot is running!</div>
        <p>Last ping: <span id="time">""" + time.strftime("%H:%M:%S") + """</span></p>
        <p><a href="/ping">Ping test</a> | <a href="/health">Health check</a></p>
    </body>
    </html>
    """

@app.route('/ping')
def ping():
    return "🏓 pong"

@app.route('/health')
def health():
    return "✅ OK"

@app.route('/status')
def status():
    return {"status": "running", "timestamp": time.time()}

def run_flask():
    """Запуск Flask сервера"""
    print("🚀 Запуск Flask сервера...")
    app.run(host='0.0.0.0', port=8080)

# ====================== АВТО-ПИНГ ======================
class AutoPinger:
    def __init__(self):
        self.last_ping = time.time()
        self.running = True
        
    def ping_self(self):
        """Пингует сам себя"""
        try:
            # Пробуем разные URL
            urls = [
                f"https://{os.environ.get('REPL_SLUG')}.{os.environ.get('REPL_OWNER')}.repl.co",
                "http://0.0.0.0:8080",
                "http://localhost:8080"
            ]
            
            for url in urls:
                try:
                    response = requests.get(f"{url}/ping", timeout=5)
                    if response.status_code == 200:
                        self.last_ping = time.time()
                        print(f"✅ Авто-пинг успешен: {time.strftime('%H:%M:%S')}")
                        return True
                except:
                    continue
            
            print("⚠️  Не удалось выполнить авто-пинг")
            return False
            
        except Exception as e:
            print(f"⚠️  Ошибка авто-пинга: {e}")
            return False
    
    def start(self):
        """Запускает авто-пинг в отдельном потоке"""
        def ping_loop():
            while self.running:
                self.ping_self()
                time.sleep(45)  # Пингуем каждые 45 секунд
        
        thread = threading.Thread(target=ping_loop)
        thread.daemon = True
        thread.start()
        print("✅ Авто-пинг запущен (каждые 45 секунд)")

# ====================== TELEGRAM БОТ ======================
def run_telegram_bot():
    """Запуск Telegram бота"""
    print("\n" + "="*50)
    print("🤖 ЗАПУСК TELEGRAM БОТА")
    print("="*50)
    
    # Импортируем здесь, чтобы Flask успел запуститься
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
        from telegram.ext import Application, CommandHandler, ContextTypes
        
        # Ваш токен и URL
        TOKEN = BOT_TOKEN
        GAME_URL_LOCAL = GAME_URL
        
        async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Обработчик /start"""
            keyboard = [[InlineKeyboardButton("🎮 НАЧАТЬ ИГРУ", web_app=WebAppInfo(url=GAME_URL_LOCAL))]]
            
            await update.message.reply_text(
                f"Привет! 🎮\n\nНажмите кнопку для игры Arrows Pro Ultra!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        # Создаем и запускаем бота
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start_command))
        
        print(f"✅ Telegram бот запущен")
        print(f"🔗 Ссылка: https://t.me/{app.bot.username}")
        print("⏳ Ожидание сообщений...")
        print("="*50)
        
        app.run_polling()
        
    except ImportError:
        print("❌ Библиотека python-telegram-bot не установлена")
        print("Установите: pip install python-telegram-bot")
    except Exception as e:
        print(f"❌ Ошибка Telegram бота: {e}")

# ====================== ОСНОВНОЙ ЗАПУСК ======================
def main():
    """Основная функция запуска"""
    print("="*60)
    print("🚀 ARROWS PRO ULTRA BOT - АВТО-ПИНГ ВКЛЮЧЕН")
    print("="*60)
    
    # 1. Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    time.sleep(2)  # Даем Flask время на запуск
    
    # 2. Запускаем авто-пинг
    pinger = AutoPinger()
    pinger.start()
    
    # 3. Пингуем сразу для проверки
    print("🔍 Первый тестовый пинг...")
    if pinger.ping_self():
        print("✅ Система авто-пинга работает!")
    else:
        print("⚠️  Проверьте настройки авто-пинга")
    
    # 4. Запускаем Telegram бота
    print("\n" + "="*50)
    print("🎮 ЗАПУСК ОСНОВНОГО БОТА")
    print("="*50)
    
    run_telegram_bot()

# ====================== АЛЬТЕРНАТИВА: ПРОСТОЙ БОТ БЕЗ БИБЛИОТЕК ======================
def run_simple_bot():
    """Простой бот без библиотек"""
    import requests as req
    
    print("\n🤖 ЗАПУСК ПРОСТОГО БОТА...")
    
    last_update_id = 0
    
    while True:
        try:
            # Получаем обновления
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            response = req.get(url, params={"offset": last_update_id, "timeout": 30})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result"):
                    for update in data["result"]:
                        last_update_id = update["update_id"] + 1
                        
                        if "message" in update:
                            msg = update["message"]
                            chat_id = msg["chat"]["id"]
                            text = msg.get("text", "")
                            
                            if text == "/start":
                                # Отправляем ответ
                                keyboard = {
                                    "inline_keyboard": [[
                                        {"text": "🎮 ИГРАТЬ", "web_app": {"url": GAME_URL}}
                                    ]]
                                }
                                
                                send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                                req.post(send_url, json={
                                    "chat_id": chat_id,
                                    "text": "🎮 Arrows Pro Ultra!\n\nНажмите кнопку:",
                                    "reply_markup": keyboard
                                })
                                print(f"📨 Отправлен ответ пользователю {chat_id}")
            
            # Небольшая пауза
            time.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    import os
    
    # Проверяем, на Replit ли мы
    if 'REPL_SLUG' in os.environ:
        print(f"✅ Запуск на Replit: {os.environ.get('REPL_SLUG')}")
        print(f"🔗 Ваш URL: https://{os.environ.get('REPL_SLUG')}.{os.environ.get('REPL_OWNER')}.repl.co")
    else:
        print("⚠️  Запуск не на Replit, авто-пинг может не работать")
    
    # Запускаем основную функцию
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("🔄 Запуск простого бота...")
        run_simple_bot()
