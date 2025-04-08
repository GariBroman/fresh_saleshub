import logging
import asyncio
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Constants
FOLLOW_UP_DELAY = 5 * 60  # 5 minutes in seconds
FOLLOW_UP_MESSAGE = """✅Лучшее время начать – сейчас!  
Не дайте конкурентам опередить Вас

Если хотите внедрить такой инструмент в свой бизнес – напишите нашему нейро-сотруднику. Он задаст несколько квалификационных вопросов и передаст информацию менеджеру.

⚡ Жмите кнопку и начните прямо сейчас!"""

# Dictionary to track scheduled tasks by user_id to avoid duplicates
scheduled_tasks = {}

async def schedule_follow_up_message(bot: Bot, chat_id: int, user_id: int):
    """Schedule a follow-up message to be sent after the specified delay"""
    
    # If a task is already scheduled for this user, don't schedule another one
    if user_id in scheduled_tasks and not scheduled_tasks[user_id].done():
        logging.info(f"Follow-up message already scheduled for user {user_id}")
        return
    
    # Create and store the task
    task = asyncio.create_task(send_delayed_follow_up(bot, chat_id, user_id))
    scheduled_tasks[user_id] = task
    logging.info(f"Scheduled follow-up message for user {user_id} in {FOLLOW_UP_DELAY} seconds")

async def send_delayed_follow_up(bot: Bot, chat_id: int, user_id: int):
    """Send a follow-up message after a delay"""
    try:
        # Wait for the specified delay
        await asyncio.sleep(FOLLOW_UP_DELAY)
        
        # Create keyboard with a button to the manager bot
        keyboard = InlineKeyboardBuilder()
        keyboard.row(InlineKeyboardButton(
            text="💬 Написать нейро-сотруднику", 
            url="https://t.me/airabbitsaler_bot"
        ))
        
        # Send the message
        await bot.send_message(
            chat_id=chat_id,
            text=FOLLOW_UP_MESSAGE,
            reply_markup=keyboard.as_markup()
        )
        
        logging.info(f"Sent follow-up message to user {user_id}")
    except Exception as e:
        logging.error(f"Error sending follow-up message to user {user_id}: {e}")
    finally:
        # Clean up the task reference
        if user_id in scheduled_tasks:
            del scheduled_tasks[user_id] 