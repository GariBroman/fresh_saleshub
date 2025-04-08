import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart

from app.config import BOT_TOKEN
from app.handlers import router
from app.db import init_db, close_db, log_user
from app.handlers.scheduled import schedule_follow_up_message

# Конфигурация логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

# Установка уровня логирования для специфических библиотек
logging.getLogger('aiogram').setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('aiohttp').setLevel(logging.INFO)

# Список команд бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь по использованию бота")
    ]
    await bot.set_my_commands(commands)

# Diagnostic middleware for messages
async def diagnostic_message_middleware(handler, event, data):
    if isinstance(event, Message) and event.from_user:
        user_id = event.from_user.id
        logging.debug(f"DIAGNOSTIC: Processing message from user_id={user_id}")
    return await handler(event, data)

# Diagnostic middleware for callback queries
async def diagnostic_callback_middleware(handler, event, data):
    if isinstance(event, CallbackQuery) and event.from_user:
        user_id = event.from_user.id
        logging.debug(f"DIAGNOSTIC: Processing callback from user_id={user_id}")
    return await handler(event, data)

# Middleware для логирования пользователей из сообщений
async def message_logging_middleware(handler, event, data):
    # Log the user if message has from_user
    if isinstance(event, Message) and event.from_user:
        # Log the user and get whether this is a new user
        success, is_new_user = await log_user(
            user_id=event.from_user.id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name,
            chat_id=event.chat.id
        )
        
        # If this is a new user, schedule a follow-up message
        if success and is_new_user:
            bot = data.get('bot')
            if bot:
                await schedule_follow_up_message(
                    bot=bot,
                    chat_id=event.chat.id,
                    user_id=event.from_user.id
                )
            else:
                logging.error("Bot object not found in middleware data")
    
    # Continue processing
    return await handler(event, data)

# Middleware для логирования пользователей из callback query (кнопки)
async def callback_logging_middleware(handler, event, data):
    # Log the user if callback has from_user
    if isinstance(event, CallbackQuery) and event.from_user:
        # Log the user and get whether this is a new user
        success, is_new_user = await log_user(
            user_id=event.from_user.id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name,
            chat_id=event.message.chat.id
        )
        
        # If this is a new user, schedule a follow-up message
        if success and is_new_user:
            bot = data.get('bot')
            if bot:
                await schedule_follow_up_message(
                    bot=bot,
                    chat_id=event.message.chat.id,
                    user_id=event.from_user.id
                )
            else:
                logging.error("Bot object not found in middleware data")
    
    # Continue processing
    return await handler(event, data)

# Основная функция запуска бота
async def main():
    # Инициализация базы данных
    await init_db()
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Добавляем diagnostic middleware
    dp.message.middleware(diagnostic_message_middleware)
    dp.callback_query.middleware(diagnostic_callback_middleware)
    
    # Добавляем middleware для логирования пользователей
    dp.message.middleware(message_logging_middleware)
    dp.callback_query.middleware(callback_logging_middleware)
    
    # Регистрация роутеров
    dp.include_router(router)
    
    # Установка команд
    await set_commands(bot)
    
    # Запуск поллинга
    logging.info("Бот AIRabbit запущен")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        # Закрываем соединение с базой данных при завершении
        await close_db()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}", exc_info=True) 