import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import config
from database import init_db
from handlers import all_routers

# Настройка красивого логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ProxGriefBot")


async def setup_bot_commands(bot: Bot):
    """Регистрация подсказок команд в Telegram."""
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="help", description="📖 Справка и помощь"),
        BotCommand(command="ticket", description="👨‍💻 Создать обращение"),
        BotCommand(command="close", description="🔒 Закрыть текущее обращение"),
        BotCommand(command="admin", description="⚡ Панель администратора"),
        BotCommand(command="stats", description="📊 Статистика тикетов")
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("Команды бота успешно зарегистрированы в меню Telegram.")
    except Exception as e:
        logger.warning(f"Не удалось установить команды меню: {e}")


async def main():
    logger.info(f"Запуск системы техподдержки сервера {config.SERVER_NAME}...")

    # Проверка наличия валидного токена бота
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "="*70 + "\n"
            "❌ ОШИБКА: Токен Telegram-бота не указан!\n\n"
            "1. Откройте файл .env в папке проекта.\n"
            "2. Найдите строку BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE\n"
            "3. Замените на токен вашего бота от @BotFather\n"
            "4. В строке ADMIN_IDS укажите ваш Telegram ID (узнать в @userinfobot)\n"
            "5. В строке AI_API_KEY укажите ключ ИИ (OpenAI, Gemini, DeepSeek и др.)\n"
            "="*70
        )
        return

    # 1. Инициализация базы данных
    logger.info("Инициализация базы данных SQLite...")
    await init_db()

    # 2. Инициализация бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # 3. Подключение всех роутеров
    for router in all_routers:
        dp.include_router(router)
    logger.info(f"Зарегистрировано {len(all_routers)} модулей маршрутизации.")

    # 4. Установка команд меню
    await setup_bot_commands(bot)

    # 5. Сброс старых вебхуков и запуск поллинга
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот @{bot_info.username} успешно авторизован и готов к работе!")
        logger.info(f"🎮 Сервер: {config.SERVER_NAME} | Админов в конфиге: {len(config.ADMIN_IDS)}")
        if config.AI_API_KEY and config.AI_API_KEY != "YOUR_AI_API_KEY_HERE":
            logger.info(f"🧠 ИИ-помощник подключен: модель {config.AI_MODEL}")
        else:
            logger.info("ℹ️ ИИ-помощник работает в режиме встроенной базы знаний (API ключ пока не указан в .env).")

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка работы бота: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Сессия бота закрыта. Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен пользователем.")

