import os
import json
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ChatMemberStatus
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
DATA_FILE = "/home/malollas/arrows_data.json"
CHANNEL_ID = "@arrows_game"  # Канал для обязательной подписки
GAME_URL = "https://7fq259fwxr-byte.github.io/arrowgame/"
SUPPORT_BOT = "@arrow_game_supprot_bot"

# Вспомогательные функции для базы данных
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

# Функция проверки подписки на канал
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Проверяет, подписан ли пользователь на канал."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки для {user_id}: {e}")
        return False

# Функция получения статистики пользователя
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

# Функция получения лидерборда
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

# Функция сохранения/обновления пользователя
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

# Главное меню
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎮 Играть", web_app=WebAppInfo(url=GAME_URL))],
        [
            InlineKeyboardButton("📊 Статистика", callback_data='stats'),
            InlineKeyboardButton("🏆 Лидерборд", callback_data='leaderboard')
        ],
        [
            InlineKeyboardButton("❓ Об игре", callback_data='about'),
            InlineKeyboardButton("🛠 Поддержка", callback_data='support')
        ],
        [InlineKeyboardButton("💡 Предложить идею", callback_data='suggestion')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для проверки подписки
def get_subscription_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}"),
            InlineKeyboardButton("✅ Я подписался", callback_data='check_subscription')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Кнопка "Назад"
def get_back_button():
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    return InlineKeyboardMarkup(keyboard)

# Команда /start с проверкой подписки
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name or "Гость"
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, context)
    
    if not is_subscribed:
        # Показываем сообщение с требованием подписки
        await update.message.reply_text(
            "⚠️ *ДОСТУП ЗАКРЫТ*\n\n"
            "Для использования бота необходима подписка на наш канал!\n\n"
            "📢 *Arrows Game Channel*: @arrows_game\n\n"
            "1. Нажмите кнопку '📢 Подписаться на канал' ниже\n"
            "2. После вступления нажмите '✅ Я подписался'\n"
            "3. Если бот не видит подписку, подождите 10 секунд и попробуйте снова",
            reply_markup=get_subscription_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # Сохраняем пользователя
    save_user_data(user_id, username)
    
    # Показываем главное меню
    welcome_text = f"""🎮 *Добро пожаловать в Arrows Pro Ultra, {username}!* 🎮

*Доступ открыт!* ✅ Вы подписаны на канал @arrows_game

*Выберите действие:*"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

# Функция показа главного меню (для callback)
async def show_main_menu(query):
    user = query.from_user
    username = user.username or user.first_name or "Гость"
    
    welcome_text = f"""🎮 *Главное меню Arrows Pro Ultra* 🎮

*Игрок:* {username}
*Статус:* ✅ Подписка активна

*Выберите действие:*"""
    
    await query.edit_message_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Проверяем подписку для всех действий, кроме проверки подписки и "назад"
    if query.data not in ['check_subscription', 'back']:
        is_subscribed = await check_subscription(user_id, context)
        if not is_subscribed:
            await query.edit_message_text(
                "❌ *ДОСТУП ОТКЛЮЧЕН*\n\n"
                "Ваша подписка на канал @arrows_game не активна!\n\n"
                "Обновите подписку и нажмите кнопку ниже:",
                reply_markup=get_subscription_keyboard(),
                parse_mode='Markdown'
            )
            return
    
    # Обработка действий
    if query.data == 'stats':
        stats = get_user_stats(user_id)
        if stats:
            stats_text = f"""📊 *ВАША СТАТИСТИКА*

👤 *Игрок:* {stats['username']}
🏆 *Уровень:* {stats['level']}
⭐ *Очки:* {stats['score']}
💰 *Монеты:* {stats['coins']}
🎮 *Игр сыграно:* {stats['games_played']}
🕐 *Последняя активность:* {stats['last_active']}"""
        else:
            stats_text = "Вы еще не начали играть! Нажмите '🎮 Играть', чтобы начать."
        
        await query.edit_message_text(
            stats_text,
            parse_mode='Markdown',
            reply_markup=get_back_button()
        )
    
    elif query.data == 'leaderboard':
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
        
        await query.edit_message_text(
            leaderboard_text,
            parse_mode='Markdown',
            reply_markup=get_back_button()
        )
    
    elif query.data == 'about':
        about_text = f"""🎮 *ARROWS PRO ULTRA*

*ОБ ИГРЕ:*
Arrows Pro Ultra - увлекательная логическая игра, где нужно расставлять стрелки на поле так, чтобы они не сталкивались.

*ОСНОВНЫЕ МЕХАНИКИ:*
• 🎯 Расставляйте стрелки на игровом поле
• 🚫 Избегайте столкновений стрелок
• 📈 Проходите уровни и повышайте сложность
• 💰 Зарабатывайте монеты за победы
• 🏆 Соревнуйтесь с другими игроками

*ОСОБЕННОСТИ:*
✅ Простой и понятный геймплей
✅ Постепенно возрастающая сложность
✅ Система достижений и монет
✅ Таблица лидеров
✅ Регулярные обновления

*ОБЯЗАТЕЛЬНО:* Подписка на канал @arrows_game

Для начала игры нажмите '🎮 Играть' в главном меню!"""
        
        await query.edit_message_text(
            about_text,
            parse_mode='Markdown',
            reply_markup=get_back_button()
        )
    
    elif query.data == 'support':
        support_text = f"""🛠 *ПОДДЕРЖКА*

*Если у вас возникли проблемы с игрой или есть вопросы:*

👨‍💻 *Техническая поддержка:* {SUPPORT_BOT}

*Мы поможем с:*
• 🐛 Техническими проблемами
• ❓ Вопросами по геймплею
• 🔧 Неполадками в игре
• 📱 Проблемами с запуском
• 📢 Вопросами по подписке на канал

*Время ответа:* обычно в течение 24 часов

*Не стесняйтесь обращаться, мы всегда рады помочь!* 😊"""
        
        await query.edit_message_text(
            support_text,
            parse_mode='Markdown',
            reply_markup=get_back_button()
        )
    
    elif query.data == 'suggestion':
        suggestion_text = f"""💡 *ПРЕДЛОЖИТЬ ИДЕЮ*

*У вас есть идея, как улучшить игру? Мы будем рады её услышать!*

📝 *Отправляйте свои предложения:* {SUPPORT_BOT}

*Что можно предложить:*
• 🎮 Новые механики геймплея
• 🎨 Улучшения интерфейса
• 📊 Дополнительные статистики
• 🏆 Новые достижения
• 🔧 Технические улучшения

*Наши критерии:*
✅ Идея должна быть оригинальной
✅ Предложение должно быть детальным
✅ Учитывайте баланс игры

*Лучшие идеи будут реализованы в следующих обновлениях!*"""
        
        await query.edit_message_text(
            suggestion_text,
            parse_mode='Markdown',
            reply_markup=get_back_button()
        )
    
    elif query.data == 'check_subscription':
        # Проверяем подписку
        is_subscribed = await check_subscription(user_id, context)
        
        if is_subscribed:
            # Сохраняем пользователя
            user = query.from_user
            save_user_data(user.id, user.username or user.first_name or "Гость")
            
            await show_main_menu(query)
        else:
            # Подписка не обнаружена
            await query.edit_message_text(
                "❌ *ПОДПИСКА НЕ ОБНАРУЖЕНА!*\n\n"
                "*Убедитесь, что вы:*\n"
                "1. Действительно вступили в канал: @arrows_game\n"
                "2. Нажали кнопку '✅ Я подписался' после вступления\n"
                "3. Если только что подписались, подождите 10 секунд\n\n"
                "*Если проблема persists:*\n"
                "• Проверьте, не вышел ли вы случайно из канала\n"
                "• Убедитесь, что канал публичный\n"
                "• Попробуйте начать снова с /start",
                reply_markup=get_subscription_keyboard(),
                parse_mode='Markdown'
            )
    
    elif query.data == 'back':
        await show_main_menu(query)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        await update.message.reply_text(
            "❌ *ДОСТУП ЗАКРЫТ*\n\n"
            "Для использования бота необходима подписка на канал @arrows_game\n\n"
            "Подпишитесь и попробуйте снова с /start",
            parse_mode='Markdown'
        )
        return
    
    help_text = f"""📚 *ДОСТУПНЫЕ КОМАНДЫ*

/start - Запустить бота и показать главное меню
/help - Показать это сообщение помощи
/stats - Показать вашу статистику
/leaderboard - Показать таблицу лидеров

*ОСНОВНЫЕ ФУНКЦИИ:*
• 🎮 Играть - Запустить игру в мини-приложении
• 📊 Статистика - Посмотреть вашу статистику
• 🏆 Лидерборд - Таблица лучших игроков
• ❓ Об игре - Информация об игре
• 🛠 Поддержка - Связь с техподдержкой
• 💡 Предложить идею - Отправить предложение по улучшению

*ОБЯЗАТЕЛЬНО:* Подписка на канал @arrows_game

*По всем вопросам:* {SUPPORT_BOT}"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Команда /stats
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        await update.message.reply_text(
            "❌ *ДОСТУП ЗАКРЫТ*\n\n"
            "Для использования бота необходима подписка на канал @arrows_game\n\n"
            "Подпишитесь и попробуйте снова с /start",
            parse_mode='Markdown'
        )
        return
    
    stats = get_user_stats(user_id)
    if stats:
        stats_text = f"""📊 *ВАША СТАТИСТИКА*

👤 *Игрок:* {stats['username']}
🏆 *Уровень:* {stats['level']}
⭐ *Очки:* {stats['score']}
💰 *Монеты:* {stats['coins']}
🎮 *Игр сыграно:* {stats['games_played']}
🕐 *Последняя активность:* {stats['last_active']}"""
    else:
        stats_text = "Вы еще не начали играть! Нажмите '🎮 Играть', чтобы начать."
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# Команда /leaderboard
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        await update.message.reply_text(
            "❌ *ДОСТУП ЗАКРЫТ*\n\n"
            "Для использования бота необходима подписка на канал @arrows_game\n\n"
            "Подпишитесь и попробуйте снова с /start",
            parse_mode='Markdown'
        )
        return
    
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
    
    await update.message.reply_text(leaderboard_text, parse_mode='Markdown')

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        await update.message.reply_text(
            "❌ *ДОСТУП ЗАКРЫТ*\n\n"
            "Для использования бота необходима подписка на канал @arrows_game\n\n"
            "Используйте /start для начала работы",
            parse_mode='Markdown'
        )
        return
    
    if text in ['статистика', 'стата', 'stats', 'stat']:
        await stats_command(update, context)
    elif text in ['лидерборд', 'лидеры', 'топ', 'leaderboard', 'top']:
        await leaderboard_command(update, context)
    elif text in ['помощь', 'хелп', 'help', 'commands']:
        await help_command(update, context)
    elif text in ['играть', 'game', 'play', 'старт']:
        await update.message.reply_text(
            "🎮 *Запуск игры*\n\n"
            "Нажмите кнопку ниже, чтобы начать игру:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 Играть", web_app=WebAppInfo(url=GAME_URL))]
            ]),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "🤔 *Не понимаю ваше сообщение*\n\n"
            "Используйте /start для отображения меню или /help для помощи.",
            parse_mode='Markdown'
        )

# Основная функция запуска бота
async def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    
    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

# Точка входа
if __name__ == '__main__':
    print("🚀 Запуск бота Arrows Pro Ultra...")
    print(f"📢 Канал для подписки: {CHANNEL_ID}")
    print(f"🎮 URL игры: {GAME_URL}")
    print(f"🛠 Бот поддержки: {SUPPORT_BOT}")
    
    # Запускаем асинхронную главную функцию
    asyncio.run(main())
