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

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка поста в канал с кнопкой калькулятора (только для админа)"""
    # Список разрешенных юзернеймов (без @)
    ADMIN_USERNAMES = ["Mikleivanovich", "mikleivanovich"] 
    
    user = update.effective_user
    print(f"Post command received from user: {user.username} (ID: {user.id})")
    
    if not user.username or user.username.lower() not in [u.lower() for u in ADMIN_USERNAMES]:
        # Отправляем сообщение об ошибке только в ЛС, чтобы не спамить
        await update.message.reply_text(f"⛔ У вас нет прав. Ваш юзернейм: @{user.username}")
        print(f"Access denied for user {user.username}")
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
        keyboard = [
            [InlineKeyboardButton(
                "📊 Открыть Инвестиционный Калькулятор",
                web_app=WebAppInfo(url=WEBAPP_URL)
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
    application.add_handler(CommandHandler("post", post_command))
    
    # Запускаем бота
    print("Bot is running!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
