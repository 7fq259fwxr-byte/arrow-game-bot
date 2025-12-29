#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arrows Pro Ultra Bot - Полная версия без библиотек
Работает на чистом Python + requests
"""

import requests
import time
import json
import logging
from datetime import datetime
import threading

# ====================== КОНФИГУРАЦИЯ ======================
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
GAME_URL = "https://7fq259fwxr-byte.github.io/arrows-game/"
SUPPORT_BOT = "@arrow_game_support_bot"

# ====================== ЛОГИРОВАНИЕ ======================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================== ТЕКСТЫ СООБЩЕНИЙ ======================
WELCOME_MESSAGE = f"""
🎮 *Arrows Pro Ultra v19*

*Увлекательная головоломка со стрелками!*

🌟 *ОСОБЕННОСТИ:*
• 100+ уровней с растущей сложностью
• Динамическое увеличение игрового поля
• Система жизней и восстановления
• Эффекты победы с конфетти
• Поддержка 3 языков
• Работает офлайн после загрузки

📱 *КАК ЗАПУСТИТЬ НА iOS:*
1. Нажмите кнопку "🎮 НАЧАТЬ ИГРУ"
2. В открывшемся окне нажмите ⋯
3. Выберите "На экран 'Домой'"
4. Нажмите "Добавить"

🔄 *УПРАВЛЕНИЕ:*
• Нажимайте на стрелки, чтобы убрать их
• Избегайте столкновений стрелок
• Проходите уровни и открывайте новые!

⚡ *Игра сохраняет прогресс автоматически!*

🆘 *Помощь и поддержка:* {SUPPORT_BOT}
"""

HELP_MESSAGE = f"""
📚 *КОМАНДЫ БОТА:*
/start - Запустить бота и показать меню
/game - Открыть игру напрямую
/help - Показать эту справку
/stats - Статистика игры
/about - Информация об игре
/support - Связаться с поддержкой

❓ *ЧАСТЫЕ ВОПРОСЫ:*

*Q: Игра не открывается на iPhone?*
A: Используйте Safari браузер и добавьте на домашний экран.

*Q: Прогресс не сохраняется?*
A: Игра использует localStorage браузера.

*Q: Как играть?*
A: Нажимайте на стрелки в правильном порядке.

*Q: Нашел баг или есть предложение?*
A: Напишите в поддержку: {SUPPORT_BOT}

🆘 *Техническая поддержка:* {SUPPORT_BOT}
"""

STATS_MESSAGE = f"""
📊 *СТАТИСТИКА ARROWS PRO ULTRA:*

• Уровни сложности: 100+
• Максимальный размер поля: 9x9
• Поддерживаемые языки: 3
• Система жизней: 3 + восстановление
• Эффекты: 15+ анимаций

🎯 *ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ:*
• Платформа: Web (PWA)
• Совместимость: iOS 12+, Android 8+
• Офлайн-режим: Да

🔄 *ПОСЛЕДНЕЕ ОБНОВЛЕНИЕ:*
• Исправлена генерация уровней
• Добавлены новые эффекты
• Улучшена производительность

🌟 *Игра полностью бесплатна и без рекламы!*

🆘 *Поддержка:* {SUPPORT_BOT}
"""

# ====================== ФУНКЦИИ ДЛЯ РАБОТЫ С TELEGRAM API ======================

def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return None

def edit_message_text(chat_id, message_id, text, reply_markup=None, parse_mode="Markdown"):
    """Редактирование сообщения"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка редактирования сообщения: {e}")
        return None

def answer_callback_query(callback_query_id, text=None, show_alert=False):
    """Ответ на callback запрос"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    
    payload = {
        "callback_query_id": callback_query_id
    }
    
    if text:
        payload["text"] = text
    
    if show_alert:
        payload["show_alert"] = True
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка ответа на callback: {e}")
        return None

def get_updates(offset=None, timeout=30):
    """Получение обновлений от Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    params = {
        "timeout": timeout,
        "allowed_updates": ["message", "callback_query"]
    }
    
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(url, params=params, timeout=timeout + 5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Ошибка получения обновлений: {e}")
    
    return {"ok": False, "result": []}

# ====================== ФУНКЦИИ ДЛЯ СОЗДАНИЯ КЛАВИАТУР ======================

def create_main_keyboard():
    """Создание главной клавиатуры"""
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🎮 НАЧАТЬ ИГРУ",
                    "web_app": {"url": GAME_URL}
                }
            ],
            [
                {"text": "📊 Статистика", "callback_data": "stats"},
                {"text": "❓ Помощь", "callback_data": "help"}
            ],
            [
                {"text": "🆘 Поддержка", "url": f"https://t.me/{SUPPORT_BOT[1:]}"},
                {"text": "⭐ Оценить", "callback_data": "rate"}
            ]
        ]
    }
    return keyboard

def create_game_keyboard():
    """Клавиатура для игры"""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🚀 ЗАПУСТИТЬ ИГРУ", "web_app": {"url": GAME_URL}}
            ]
        ]
    }
    return keyboard

def create_support_keyboard():
    """Клавиатура для поддержки"""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📨 Написать в поддержку", "url": f"https://t.me/{SUPPORT_BOT[1:]}"}
            ],
            [
                {"text": "📋 Шаблон сообщения", "callback_data": "support_template"}
            ],
            [
                {"text": "🎮 Вернуться к игре", "web_app": {"url": GAME_URL}}
            ]
        ]
    }
    return keyboard

def create_back_to_game_keyboard():
    """Клавиатура 'Вернуться к игре'"""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🎮 Вернуться к игре", "web_app": {"url": GAME_URL}}
            ]
        ]
    }
    return keyboard

# ====================== ОБРАБОТЧИКИ КОМАНД ======================

def handle_start_command(chat_id, user_name, message_id=None):
    """Обработка команды /start"""
    logger.info(f"Пользователь {chat_id} ({user_name}) запустил бота")
    
    keyboard = create_main_keyboard()
    text = f"Привет, {user_name}! 👋\n\n{WELCOME_MESSAGE}"
    
    if message_id:
        return edit_message_text(chat_id, message_id, text, keyboard)
    else:
        return send_message(chat_id, text, keyboard)

def handle_help_command(chat_id, message_id=None):
    """Обработка команды /help"""
    keyboard = create_support_keyboard()
    
    if message_id:
        return edit_message_text(chat_id, message_id, HELP_MESSAGE, keyboard)
    else:
        return send_message(chat_id, HELP_MESSAGE, keyboard)

def handle_game_command(chat_id, message_id=None):
    """Обработка команды /game"""
    keyboard = create_game_keyboard()
    text = "Нажмите кнопку ниже, чтобы сразу начать игру:"
    
    if message_id:
        return edit_message_text(chat_id, message_id, text, keyboard)
    else:
        return send_message(chat_id, text, keyboard)

def handle_stats_command(chat_id, message_id=None):
    """Обработка команды /stats"""
    keyboard = create_back_to_game_keyboard()
    
    if message_id:
        return edit_message_text(chat_id, message_id, STATS_MESSAGE, keyboard)
    else:
        return send_message(chat_id, STATS_MESSAGE, keyboard)

def handle_support_command(chat_id, message_id=None):
    """Обработка команды /support"""
    support_text = f"""
🆘 *ТЕХНИЧЕСКАЯ ПОДДЕРЖКА*

Для быстрого решения проблемы:
1. Нажмите кнопку ниже для связи
2. Опишите проблему подробно
3. Укажите ваше устройство и браузер

*ЧТО УКАЗАТЬ В СООБЩЕНИИ:*
• Описание проблемы
• Устройство (iPhone 12, Samsung S21 и т.д.)
• Браузер (Safari, Chrome)
• Версия ОС
• Что вы делали перед ошибкой

*ОТВЕТ:*
• Обычно в течение 24 часов
• Рабочие дни: Пн-Пт, 10:00-18:00

*БЫСТРАЯ СВЯЗЬ:* {SUPPORT_BOT}
"""
    
    keyboard = create_support_keyboard()
    
    if message_id:
        return edit_message_text(chat_id, message_id, support_text, keyboard)
    else:
        return send_message(chat_id, support_text, keyboard)

# ====================== ОБРАБОТЧИКИ CALLBACK КНОПОК ======================

def handle_callback_query(callback_query):
    """Обработка нажатий на кнопки"""
    query_id = callback_query["id"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    data = callback_query["data"]
    user = callback_query["from"]
    
    logger.info(f"Пользователь {user['id']} нажал кнопку: {data}")
    
    # Отвечаем на callback
    answer_callback_query(query_id)
    
    if data == "stats":
        handle_stats_command(chat_id, message_id)
    
    elif data == "help":
        handle_help_command(chat_id, message_id)
    
    elif data == "rate":
        rate_text = "⭐ *Оцените игру!*\n\nЕсли вам нравится игра, поделитесь ей с друзьями!\n\n*Ваша оценка помогает развитию игры!* ❤️\n\nЕсть идеи или нашли баг? Напишите в поддержку!"
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🎮 Продолжить игру", "web_app": {"url": GAME_URL}}
                ],
                [
                    {"text": "📢 Поделиться", "url": "https://t.me/share/url?url=https://t.me/ArrowsProUltraBot&text=🎮 Попробуй крутую игру Arrows Pro Ultra!"}
                ],
                [
                    {"text": "🆘 Сообщить о проблеме", "url": f"https://t.me/{SUPPORT_BOT[1:]}"}
                ]
            ]
        }
        
        edit_message_text(chat_id, message_id, rate_text, keyboard)
    
    elif data == "support_template":
        template = f"""
*ШАБЛОН ДЛЯ ТЕХПОДДЕРЖКИ:*

*Проблема:* [Опишите проблему]
*Устройство:* [Например: iPhone 13]
*Браузер:* [Например: Safari]
*Версия ОС:* [Например: iOS 16.5]
*Действия перед ошибкой:* [Что вы делали]

*Дополнительно:*
• Скриншоты приложены: [Да/Нет]
• Уровень игры: [Номер уровня]
• Описание бага: [Подробно]

*Контакт для связи:* @{user.get('username', 'не указан')}

---
Отправьте это сообщение в поддержку: {SUPPORT_BOT}
        """
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📨 Отправить в поддержку", "url": f"https://t.me/{SUPPORT_BOT[1:]}?text=Проблема с игрой Arrows Pro Ultra"}
                ],
                [
                    {"text": "🎮 Вернуться к игре", "web_app": {"url": GAME_URL}}
                ]
            ]
        }
        
        edit_message_text(chat_id, message_id, template, keyboard)

# ====================== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ======================

def handle_text_message(chat_id, text, user_name):
    """Обработка текстовых сообщений"""
    text_lower = text.lower()
    
    # Ключевые слова для определения проблем
    error_keywords = ['ошибка', 'баг', 'не работает', 'сломалось', 'глюк', 'проблема']
    
    if any(word in text_lower for word in error_keywords):
        error_text = f"""
⚠️ *Похоже, у вас возникла проблема с игрой!*

Для быстрого решения:
1. Напишите в поддержку: {SUPPORT_BOT}
2. Опишите проблему подробно
3. Укажите устройство и браузер

*Поддержка ответит в течение 24 часов!*
        """
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🆘 Написать в поддержку", "url": f"https://t.me/{SUPPORT_BOT[1:]}"}
                ],
                [
                    {"text": "📋 Шаблон для поддержки", "callback_data": "support_template"}
                ]
            ]
        }
        
        send_message(chat_id, error_text, keyboard)
    
    elif 'спасибо' in text_lower or 'thanks' in text_lower:
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "⭐ Оценить игру", "callback_data": "rate"}
                ]
            ]
        }
        send_message(chat_id, "Спасибо за отзыв! Рады, что вам нравится! ❤️", keyboard)
    
    else:
        keyboard = create_main_keyboard()
        send_message(chat_id, 
                    f"Я бот для игры Arrows Pro Ultra! 🎮\n\n"
                    f"Используйте команды или кнопки для навигации.\n"
                    f"Если есть проблемы - пишите в поддержку: {SUPPORT_BOT}", 
                    keyboard)

# ====================== ОСНОВНАЯ ФУНКЦИЯ ======================

def main():
    """Основная функция бота"""
    print("=" * 60)
    print("🤖 БОТ ARROWS PRO ULTRA ЗАПУЩЕН (без библиотек!)")
    print("=" * 60)
    print(f"🎮 Игра: {GAME_URL}")
    print(f"🆘 Поддержка: {SUPPORT_BOT}")
    print("=" * 60)
    print("⏳ Ожидание сообщений...")
    print("=" * 60)
    
    last_update_id = None
    
    while True:
        try:
            # Получаем обновления
            updates = get_updates(last_update_id, timeout=30)
            
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"] + 1
                    
                    # Обработка callback запросов (нажатия на кнопки)
                    if "callback_query" in update:
                        handle_callback_query(update["callback_query"])
                    
                    # Обработка текстовых сообщений
                    elif "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        user_name = message["chat"].get("first_name", "Пользователь")
                        
                        # Текстовые сообщения
                        if "text" in message:
                            text = message["text"]
                            
                            # Обработка команд
                            if text.startswith("/"):
                                command = text.split()[0].lower()
                                
                                if command == "/start":
                                    handle_start_command(chat_id, user_name)
                                
                                elif command == "/help":
                                    handle_help_command(chat_id)
                                
                                elif command == "/game":
                                    handle_game_command(chat_id)
                                
                                elif command == "/stats":
                                    handle_stats_command(chat_id)
                                
                                elif command == "/support":
                                    handle_support_command(chat_id)
                                
                                else:
                                    handle_text_message(chat_id, text, user_name)
                            
                            # Обычные текстовые сообщения
                            else:
                                handle_text_message(chat_id, text, user_name)
            
            # Небольшая пауза между запросами
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Бот остановлен пользователем")
            break
        
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(5)  # Пауза при ошибке

# ====================== ЗАПУСК ======================

if __name__ == "__main__":
    main()
