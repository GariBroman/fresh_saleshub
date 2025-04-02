from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards.main_kb import get_main_keyboard, get_cases_keyboard
from app.handlers.callback import WELCOME_MESSAGE

# Маршрутизатор для команды /start
router = Router()

# Сообщение с кейсами
CASES_MESSAGE = """
Твой топовый ИИ-маркетолог!

Мы скормили ему лучшие книги по маркетингу, выступления топовых маркетологов и сеньоров, успешные маркетинговые стратегии которые сработали в лучших компаниях мира.

Загрузи в него свои материалы или опиши ему свою ситуацию, поставь перед ним задачу и он все сделает за тебя!"""

# Обработчик команды /start
@router.message(Command("start"))
async def command_start(message: Message, state: FSMContext):
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