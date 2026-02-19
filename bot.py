"""
Telegram бот для запуска Mini App калькулятора инвестиций.
"""

from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')
# Имя вашего приложения в BotFather (Short Name). 
# Если вы при создании Mini App указали не 'app', поменяйте здесь.
MINI_APP_NAME = "app" 

print(f"Bot script started. Token found: {bool(TELEGRAM_BOT_TOKEN)}, WebApp URL: {WEBAPP_URL}")

if not TELEGRAM_BOT_TOKEN:
    print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN is missing!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    
    # Telegram требует HTTPS для Mini App. 
    # Если URL начинается с http://, бот выдаст ошибку при отправке кнопки.
    is_https = WEBAPP_URL.startswith('https://')
    
    if is_https:
        keyboard = [
            [InlineKeyboardButton(
                "📊 Открыть Инвестиционный Калькулятор",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            "👋 Приветствую!\n\n"
            "Это ваш персональный инвестиционный калькулятор.\n\n"
            "ℹ️ **Важно:**\n"
            "При первом запуске введите свои данные (капитал, доход, возраст и т.д.) в соответствующие поля. Бот запомнит их для вас.\n\n"
            "📈 Вы сможете:\n"
            "• Рассчитать рост капитала\n"
            "• Спланировать выход на пенсию (вручную или через 'Правило 4%')\n"
            "• Увидеть интерактивные графики с зонами безопасности\n\n"
            "Нажмите кнопку ниже, чтобы ввести данные и начать расчет! 👇"
        )
    else:
        # Фолбек сообщение, если URL не HTTPS (например, localhost)
        reply_markup = None
        welcome_message = (
            "⚠️ **Ошибка конфигурации**\n\n"
            "Telegram требует **HTTPS** для запуска Mini App. Ваш текущий URL: `" + WEBAPP_URL + "`\n\n"
            "Для тестирования используйте туннель (например, **ngrok**), чтобы получить HTTPS адрес."
        )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "📖 **Справка по калькулятору**\n\n"
        "Этот бот поможет вам рассчитать, когда вы сможете выйти на пенсию и какой капитал у вас будет.\n\n"
        "🔢 **Основные параметры:**\n"
        "• **Капитал**: ваши текущие накопления.\n"
        "• **Доход**: сколько вы зарабатываете в месяц.\n"
        "• **Расходы**: сколько вы тратите сейчас. Калькулятор использует это для расчета нужной суммы на пенсии.\n"
        "• **Доходность**: ожидаемый годовой % роста ваших инвестиций (для S&P 500 это ~8-10%).\n"
        "• **Инфляция**: на сколько в среднем растут цены в год. Калькулятор индексирует ваши расходы.\n"
        "• **Рост доходов**: на сколько ежегодно растет ваша зарплата.\n\n"
        "🏖️ **Режимы пенсии:**\n"
        "• **Вручную**: вы сами указываете желаемый возраст.\n"
        "• **Авто-поиск**: калькулятор найдет возраст, когда ваш капитал позволит жить на 4% в год (безопасный уровень вывода).\n\n"
        "Используйте /start, чтобы открыть приложение!"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка связи"""
    await update.message.reply_text("🏓 Понг! Бот на связи и работает.")

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка прав бота в канале"""
    ADMIN_ID = 775697194
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Введите имя канала: `/check @name`", parse_mode='Markdown')
        return

    chat_id = context.args[0]
    try:
        chat = await context.bot.get_chat(chat_id)
        me = await context.bot.get_chat_member(chat_id, context.bot.id)
        
        status_text = (
            f"✅ **Канал найден:** {chat.title}\n"
            f"👤 **Мой статус:** {me.status}\n"
            f"📝 **Права на пост:** {'Есть' if me.can_post_messages else 'НЕТ'}\n"
        )
        await update.message.reply_text(status_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ **Ошибка проверки:** {str(e)}\n\nУбедитесь, что канал публичный и бот там админ.")

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка поста в канал с кнопкой калькулятора (только для владельца)"""
    # Ваш числовой ID для 100% надежности
    ADMIN_ID = 775697194
    
    user = update.effective_user
    print(f"Post command received from user: {user.username} (ID: {user.id})")
    
    if user.id != ADMIN_ID:
        await update.message.reply_text(f"⛔ У вас нет прав. Ваш ID: {user.id}")
        print(f"Access denied for user ID {user.id}")
        return

    print(f"Arguments received: {context.args}")

    # Проверка аргументов: /post @channel текст
    if len(context.args) < 2:
        await update.message.reply_text(
            "📝 **Как использовать:**\n"
            "`/post @имя_канала Текст вашего поста`"
        )
        return

    channel_id = context.args[0]
    post_text = " ".join(context.args[1:])

    try:
        # Для каналов НЕЛЬЗЯ использовать прямой web_app (тип кнопки), 
        # Telegram разрешает это только в ЛС. 
        # В каналах нужно использовать обычную кнопку-ссылку на приложение бота.
        bot_info = await context.bot.get_me()
        # Ссылка вида https://t.me/bot_username/short_name
        webapp_link = f"https://t.me/{bot_info.username}/{MINI_APP_NAME}"
        
        keyboard = [
            [InlineKeyboardButton(
                "📊 Открыть Инвестиционный Калькулятор",
                url=webapp_link
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        print(f"Attempting to send message to {channel_id}...")
        await context.bot.send_message(
            chat_id=channel_id,
            text=post_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await update.message.reply_text(f"✅ Пост успешно отправлен в {channel_id}")
        print("Message sent successfully.")
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        print(error_msg)
        await update.message.reply_text(error_msg + "\n\nПроверьте, что бот админ в канале.")

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("post", post_command))
    
    # Запускаем бота
    print("Bot is starting...")
    
    # Принудительно создаем цикл событий для стабильности на Render (Python 3.12+)
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    print("Bot is running and loop is set!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
