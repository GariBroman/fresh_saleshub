from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging
import asyncpg

from app.keyboards.main_kb import get_main_keyboard, get_cases_keyboard
from app.handlers.callback import WELCOME_MESSAGE
from app.db import log_user
from app.handlers.scheduled import schedule_follow_up_message

# Маршрутизатор для команды /start
router = Router()

# Сообщение с кейсами
CASES_MESSAGE = """Твой топовый ИИ-маркетолог!🔥

Мы прокачали его лучшими книгами по маркетингу 📚, выступлениями топовых спикеров и успешными стратегиями мировых брендов 🌍

🔹 Загрузи свои материалы или опиши свою ситуацию 
🔹 Поставь задачу
🔹 Получай готовые решения! 


✅ Он всё сделает за тебя – быстро, точно и эффективно!"""

# Обработчик команды /start
@router.message(Command("start"))
async def command_start(message: Message, state: FSMContext):
    # Явно логируем пользователя при старте
    success, is_new_user = await log_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        chat_id=message.chat.id
    )
    
    # Если это новый пользователь, планируем отправку сообщения через 5 минут
    if success and is_new_user:
        await schedule_follow_up_message(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=message.from_user.id
        )
    
    # Отправляем второе сообщение с клавиатурой для кейсов (отображается первым)
    await message.answer(
        text=CASES_MESSAGE,
        reply_markup=get_cases_keyboard()
    )
    
    # Отправляем первое сообщение с основной клавиатурой (отображается вторым/последним)
    main_message = await message.answer(
        text=WELCOME_MESSAGE,
        reply_markup=get_main_keyboard()
    )
    
    # Сохраняем ID основного сообщения для возможности возврата к нему
    await state.update_data(main_message_id=main_message.message_id)
    
    # Сбрасываем состояние FSM, если оно было
    await state.clear() 