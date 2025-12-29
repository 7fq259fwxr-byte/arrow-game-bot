#!/usr/bin/env python3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler

# Токен вашего бота
TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
# URL вашей игры
GAME_URL = "https://7fq259fwxr-byte.github.io/arrows-game/"

async def start(update: Update, context):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("🎮 НАЧАТЬ ИГРУ", web_app=WebAppInfo(url=GAME_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 *Arrows Pro Ultra*\n\n"
        "Нажмите кнопку ниже, чтобы открыть игру!\n\n"
        "Для iOS: откройте в Safari → Поделиться → 'На экран Домой'",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    """Запуск бота"""
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    
    # Запускаем бота
    print("🤖 Бот запущен на Replit!")
    print(f"🔗 Ссылка: https://t.me/{app.bot.username}")
    app.run_polling()

if __name__ == "__main__":
    main()
