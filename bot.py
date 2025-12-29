#!/usr/bin/env python3
# bot_simple.py - работает без python-telegram-bot
import requests
import time
import json

TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
GAME_URL = "https://7fq259fwxr-byte.github.io/arrows-game/"

def send_message(chat_id, text):
    """Отправка сообщения с кнопкой"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[{
                "text": "🎮 НАЧАТЬ ИГРУ",
                "web_app": {"url": GAME_URL}
            }]]
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return None

def get_updates(offset=None):
    """Получение обновлений от Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(url, params=params, timeout=35)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Ошибка получения: {e}")
    
    return {}

def main():
    print("🤖 Бот запущен (простая версия)")
    print("⏳ Ожидание сообщений...")
    
    last_update_id = None
    
    while True:
        try:
            updates = get_updates(last_update_id)
            
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"] + 1
                    
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        
                        if text == "/start":
                            response = f"Привет! 🎮\n\nНажмите кнопку для игры Arrows Pro Ultra!"
                            send_message(chat_id, response)
                            print(f"📨 Ответил пользователю {chat_id}")
                        
                        elif text == "/game":
                            send_message(chat_id, "Запускайте игру:")
                            print(f"🎮 Отправлена игра пользователю {chat_id}")
            
            # Небольшая пауза
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен")
            break
        except Exception as e:
            print(f"⚠️ Ошибка в основном цикле: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
