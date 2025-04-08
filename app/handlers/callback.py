import os
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

from app.config import CATEGORIES, SOUNDS_DIR
from app.keyboards.main_kb import (
    get_main_keyboard,
    get_second_level_keyboard,
    get_voice_bots_keyboard,
    get_text_bots_keyboard,
    get_file_keyboard,
    get_demo_keyboard,
    get_contact_keyboard
)

# Настраиваем логирование
logger = logging.getLogger(__name__)

# Маршрутизатор для обработки callback
router = Router()

# Тексты для разных категорий
CATEGORY_TEXTS = {
    "voice": "🎙 Голосовые боты позволяют автоматизировать общение с клиентами через телефонные звонки.",
    "text": "💬 Текстовые боты помогают автоматизировать коммуникацию с клиентами через сообщения.",
    "media": "📷 Фото-видео боты помогают автоматизировать взаимодействие с клиентами через визуальный контент.",
    "dev": "💻 Мы разрабатываем программное обеспечение любой сложности под ваши бизнес-задачи."
}

# Тексты для категорий голосовых ботов
VOICE_CATEGORY_TEXTS = {
    "dentistry": "🦷 Голосовые боты для стоматологии:\n\n- Прием обращений в регистратуру\n- Напоминание о записи\n- Лидогенерация (приглашение новых клиентов, например на диагностику)\n- Обзвон \"спящих\" клиентов с целью активизации (бесплатный осмотр, чистка зубов и т.д.)\n- Акционные обзвоны, в честь праздников\n- SMS-рассылка с подтверждением записи\n- Запись в детскую стоматологию",
    "barbershop": "💇 Голосовые боты для салонов и барбершопов:\n\n- Обзвон клиентов (потерянных)\n- Напоминание о времени прихода в салон\n- Проведение опроса (NPS)\n- Запись клиента на конкретное время\n- Лидогенерация для салона (акции, скидки - привлечение новых клиентов)\n- HR - подбор сотрудников\n- Массажи",
    "cleaning": "🧹 Голосовые боты для клининговых компаний:\n\n- Чистка на улице\n- Чистка дома/квартиры",
    "jurisprudence": "⚖️ Голосовые боты для юридических компаний:\n\n- Работа бота на обработке у нотариуса + \n- Запись на прием/консультацию/ коллегия адвокатов+\n- Напоминание о встрече\n- NPS- опрос о качестве работы компании и юриста\n- Тел-бот для подбора специалиста в интервью",
    "realestate": "🏢 Голосовые боты для недвижимости:\n\n- Опрос по качеству услуг\n- Лидогенерация по аренде коммерческой недвижимости+\n- Пациентов обзвоны по заключением ДДС+\n- Ремонт квартир\n- Приглашение на прачную и подписание акта приема-передачи квартиры в новостройке от застройщика собственнику\n- HR - подбор сотрудников",
    "hr": "👥 Голосовые боты для HR и найма:\n\n- Обзвон базы с предложением пройти собеседование\n- Напоминание о дате и времени прихода на в день собеседования+\n- Подтверждение явки перед собеседованием\n- Информирование о приеме на работу"
}

# Тексты для текстовых ботов
TEXT_CATEGORY_TEXTS = {
    "jurisprudence": "⚖️ Текстовые боты для юридических компаний помогают автоматизировать консультации и сбор данных.",
    "beauty": "💄 Текстовые боты для салонов красоты позволяют клиентам записываться на процедуры и получать информацию.",
    "video": "🎬 Видео демонстрации наглядно показывают работу ботов в реальных условиях."
}

# Ссылки для текстовых ботов
TEXT_LINKS = {
    "jurisprudence": "https://teletype.in/@airabbit/sJtZL7jMSsD",
    "beauty": "https://teletype.in/@airabbit/l3tWUBzLmHT",
    "video": "https://rutube.ru/video/547d599dcad8a2de4318199733c6985f/"
}

# Контакты для связи
CONTACT_LINKS = {
    "default": "@maximdeveloper",
    "voice": "@airabbitsaler_bot",
    "text": "@airabbitsaler_bot",
    "media": "@maximdeveloper",
    "dev": "@maximdeveloper"
}

# Карта соответствий subcategory и ключевых слов в файлах
AUDIO_KEYWORD_MAP = {
    "registration": ["запись", "прием", "регистратур"],
    "reminder": ["напоминание", "подтверждение", "визит"],
    "promo": ["акци", "обзвон"],
    "sms": ["смс", "рассылк"],
    "kids": ["детск"],
    "lost": ["потерян", "обзвон"],
    "nps": ["nps", "опрос"],
    "appointment": ["запись", "прием"],
    "outdoor": ["улиц"],
    "indoor": ["дом", "квартир"],
    "notary": ["нотариус"],
    "specialist": ["подбор", "специалист"],
    "quality": ["качеств", "опрос"],
    "rent": ["аренд"],
    "contract": ["договор", "дду"],
    "view": ["просмотр"],
    "interview": ["собеседование"],
    "confirm": ["подтверждение", "явк"],
    "hiring": ["прием", "работ"]
}

# Приветственное сообщение (полная версия)
WELCOME_MESSAGE = """AIRabbit – эксперты по автоматизации бизнеса! 📈

Мы внедряем умных текстовых и голосовых ботов на базе ИИ, которые оптимизируют бизнес-процессы и повышают конверсию на 20-30% 🚀

Наши боты способны производить:

🔹 Лидогенерация 
🔹 Оживление клиентской базы 
🔹 Консультирование и квалификация 
🔹 Сопровождение по воронке продаж
🔹 Запись на приём и напоминания 
🔹 Отправка ссылок на оплату 

⚡ Начните использовать ИИ раньше конкурентов и увеличьте прибыль!"""

# Хранение ID отправленных аудио сообщений
sent_audio_messages = {}

# Хранение ID основного сообщения меню для каждого пользователя
main_menu_messages = {}

# Хранение состояния обработки для предотвращения одновременных нажатий
processing_states = {}

# Функция для отправки всех аудиофайлов из категории
async def send_all_audio_files(callback: CallbackQuery, category: str):
    # Проверяем, не обрабатывается ли уже запрос от этого пользователя
    user_id = callback.from_user.id
    if user_id in processing_states and processing_states[user_id]:
        logger.info(f"Пользователь {user_id} уже обрабатывает запрос, пропускаем")
        await callback.answer("Пожалуйста, подождите обработки предыдущего запроса")
        return False
    
    # Устанавливаем флаг обработки
    processing_states[user_id] = True
    
    try:
        # Формируем путь к директории
        category_dir = SOUNDS_DIR / category
        
        # Проверяем существование директории
        if not os.path.exists(category_dir):
            logger.warning(f"Директория '{category}' не найдена")
            await callback.answer("Извините, аудиозаписи для этой категории временно недоступны")
            processing_states[user_id] = False
            return False
        
        try:
            # Получаем все MP3 файлы в директории
            audio_files = [f for f in os.listdir(category_dir) if f.lower().endswith('.mp3')]
            
            if not audio_files:
                logger.warning(f"Нет аудиофайлов в директории '{category}'")
                await callback.answer("Извините, аудиозаписи для этой категории временно недоступны")
                processing_states[user_id] = False
                return False
            
            # Записываем ID пользователя для хранения списка отправленных сообщений
            sent_audio_messages[user_id] = []
            
            # Сохраняем ID основного сообщения меню
            main_menu_messages[user_id] = callback.message.message_id
            
            # Категория в читаемом формате
            category_name = CATEGORIES.get(category, category.capitalize())
            
            # Сначала редактируем основное сообщение меню, чтобы показать контекст категории
            # и добавляем кнопку "Назад"
            keyboard = InlineKeyboardBuilder()
            keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_from_audios_{category}"))
            
            # Редактируем основное сообщение
            await callback.message.edit_text(
                text=f"Примеры голосовых ботов для категории {category_name}:",
                reply_markup=keyboard.as_markup()
            )
            
            # Отправляем каждый аудиофайл отдельным сообщением
            for file in audio_files:
                audio_path = category_dir / file
                audio_file = FSInputFile(audio_path)
                
                # Отправляем аудио
                audio_message = await callback.message.answer_audio(
                    audio=audio_file,
                    caption=f"Пример: {file.replace('.mp3', '').replace('_', ' ').capitalize()}",
                    reply_markup=None
                )
                
                # Сохраняем ID отправленного сообщения
                sent_audio_messages[user_id].append(audio_message.message_id)
            
            logger.info(f"Отправлено {len(audio_files)} аудиофайлов для категории '{category}'")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке аудио: {e}", exc_info=True)
            await callback.answer("Произошла ошибка при отправке аудио")
            return False
    finally:
        # Сбрасываем флаг обработки независимо от результата
        processing_states[user_id] = False

# Функция для отправки аудио по ID категории и подкатегории
async def send_audio(callback: CallbackQuery, category: str, subcategory: str):
    # Формируем путь к директории
    category_dir = SOUNDS_DIR / category
    
    # Проверяем существование директории
    if not os.path.exists(category_dir):
        logger.warning(f"Директория '{category}' не найдена")
        await callback.answer("Извините, аудиозаписи для этой категории временно недоступны")
        return False
    
    try:
        # Получаем все MP3 файлы в директории
        audio_files = [f for f in os.listdir(category_dir) if f.lower().endswith('.mp3')]
        
        if not audio_files:
            logger.warning(f"Нет аудиофайлов в директории '{category}'")
            await callback.answer("Извините, аудиозаписи для этой категории временно недоступны")
            return False
        
        # Ищем подходящий файл по ключевым словам
        selected_file = None
        keywords = AUDIO_KEYWORD_MAP.get(subcategory, [subcategory])
        
        logger.info(f"Ищем файл для подкатегории '{subcategory}' с ключевыми словами: {keywords}")
        logger.info(f"Доступные файлы: {audio_files}")
        
        # Пытаемся найти файл по ключевым словам
        for keyword in keywords:
            for file in audio_files:
                if keyword.lower() in file.lower():
                    selected_file = file
                    logger.info(f"Найден файл по ключевому слову '{keyword}': {file}")
                    break
            if selected_file:
                break
                
        # Если не нашли ничего подходящего, берем первый файл
        if not selected_file and audio_files:
            selected_file = audio_files[0]
            logger.info(f"Подходящий файл не найден, используем первый файл: {selected_file}")
        
        if not selected_file:
            logger.warning(f"Не удалось найти подходящий файл для подкатегории '{subcategory}'")
            await callback.answer("Извините, аудиозапись для этой подкатегории временно недоступна")
            return False
        
        # Формируем путь к файлу и отправляем
        audio_path = category_dir / selected_file
        audio_file = FSInputFile(audio_path)
        
        # Отправляем аудио с кнопкой возврата
        keyboard = InlineKeyboardBuilder()
        keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_to_voice_{category}"))
        
        # Отправляем аудио
        await callback.message.answer_audio(
            audio=audio_file,
            caption=f"Пример работы голосового бота для категории {CATEGORIES.get(category, category)}",
            reply_markup=keyboard.as_markup()
        )
        logger.info(f"Отправлен аудиофайл: {selected_file}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при отправке аудио: {e}", exc_info=True)
        await callback.answer("Произошла ошибка при отправке аудио")
        return False

# Обработка основных категорий
@router.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Извлекаем категорию из callback_data
    category = callback.data.split("_")[1]
    
    # Обновляем сообщение с текстом категории и соответствующей клавиатурой
    await callback.message.edit_text(
        text=CATEGORY_TEXTS.get(category, "Выберите категорию:"),
        reply_markup=get_second_level_keyboard(category)
    )
    
    # Сохраняем выбранную категорию в состоянии
    await state.update_data(current_category=category)

# Описание ИИ-маркетолога
MARKETER_DESCRIPTION = """Твой топовый ИИ-маркетолог!🔥

Мы прокачали его лучшими книгами по маркетингу 📚, выступлениями топовых спикеров и успешными стратегиями мировых брендов 🌍

🔹 Загрузи свои материалы или опиши свою ситуацию 
🔹 Поставь задачу
🔹 Получай готовые решения! 


✅ Он всё сделает за тебя – быстро, точно и эффективно!"""

# Обработка выбора ИИ-маркетолога
@router.callback_query(F.data == "marketer_bot")
async def process_marketer_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Создаем клавиатуру с кнопкой перехода и кнопкой назад
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="🚀 Перейти к ИИ-маркетологу", url="https://t.me/marketingairabbit_bot"))
    keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    
    # Обновляем сообщение с описанием ИИ-маркетолога
    await callback.message.edit_text(
        text=MARKETER_DESCRIPTION,
        reply_markup=keyboard.as_markup()
    )

# Обработка выбора "Кейсы" для категории
@router.callback_query(F.data.startswith("cases_"))
async def process_cases_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Извлекаем категорию из callback_data
    category = callback.data.split("_")[1]
    
    # Для голосовых и текстовых ботов показываем соответствующие категории
    if category == "voice":
        keyboard = get_voice_bots_keyboard()
        text = "🎙 Выберите категорию голосового бота:"
    elif category == "text":
        keyboard = get_text_bots_keyboard()
        text = "💬 Выберите категорию текстового бота:"
    else:
        # Для всех остальных категорий показываем ИИ-маркетолога
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🤖 ИИ-маркетолог", callback_data="marketer_bot"))
        kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_to_category_{category}"))
        keyboard = kb.as_markup()
        text = "📊 Выберите интересующий вас кейс:"
    
    # Обновляем сообщение
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )

# Обработка выбора "Связь" для категории
@router.callback_query(F.data.startswith("contact_"))
async def process_contact_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Извлекаем категорию из callback_data
    category = callback.data.split("_")[1]
    
    # Обновляем сообщение с контактной информацией, используя обновленную функцию клавиатуры
    await callback.message.edit_text(
        text=f"📱 Свяжитесь с нашим менеджером для получения дополнительной информации и консультации по {CATEGORY_TEXTS.get(category, 'вашему запросу').lower()}",
        reply_markup=get_contact_keyboard(category)
    )

# Обработка выбора категории голосовых ботов
@router.callback_query(F.data.startswith("voice_"))
async def process_voice_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Извлекаем категорию из callback_data
    category = callback.data.split("_")[1]
    
    # Сохраняем ID текущего сообщения перед отправкой аудио
    await state.update_data(main_message_id=callback.message.message_id)
    
    # Сохраняем текущую подкатегорию
    await state.update_data(current_subcategory=category)
    
    # Отправляем все аудиофайлы из выбранной категории
    await send_all_audio_files(callback, category)

# Обработка выбора категории текстовых ботов (кроме демо)
@router.callback_query(lambda c: c.data.startswith("text_") and c.data != "text_demo")
async def process_text_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Проверяем, не обрабатывается ли уже запрос от этого пользователя
    user_id = callback.from_user.id
    if user_id in processing_states and processing_states[user_id]:
        logger.info(f"Пользователь {user_id} уже обрабатывает запрос, пропускаем")
        return
    
    # Устанавливаем флаг обработки
    processing_states[user_id] = True
    
    try:
        # Извлекаем категорию из callback_data
        category = callback.data.split("_")[1]
        
        # Получаем ссылку для данной категории
        link = TEXT_LINKS.get(category, "https://example.com/case.pdf")
        
        # Для презентации отправляем PDF файл
        if category == "presentation":
            try:
                # Отправляем PDF файл
                document = FSInputFile(link)
                sent_message = await callback.message.answer_document(
                    document=document,
                    caption="Презентация AIRabbit",
                    reply_markup=InlineKeyboardBuilder().row(
                        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_text")
                    ).as_markup()
                )
                
                # Сохраняем ID отправленного сообщения
                if user_id not in sent_audio_messages:
                    sent_audio_messages[user_id] = []
                sent_audio_messages[user_id].append(sent_message.message_id)
                
                # Удаляем предыдущее сообщение
                try:
                    await callback.message.delete()
                except TelegramBadRequest as e:
                    if "message to delete not found" in str(e).lower():
                        logger.info(f"Сообщение уже удалено: {callback.message.message_id}")
                    else:
                        logger.error(f"Ошибка при удалении сообщения: {e}")
            except Exception as e:
                logger.error(f"Ошибка при отправке PDF: {e}", exc_info=True)
                await callback.message.answer(
                    "Произошла ошибка при отправке презентации. Пожалуйста, попробуйте позже.",
                    reply_markup=InlineKeyboardBuilder().row(
                        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_text")
                    ).as_markup()
                )
        else:
            # Для остальных отправляем ссылку прямо в сообщении
            text = TEXT_CATEGORY_TEXTS.get(category, "Информация о текстовых ботах:")
            text += f"\n\n<a href='{link}'>Ссылка на кейс</a>"
            
            # Создаем клавиатуру только с кнопкой назад
            keyboard = InlineKeyboardBuilder()
            keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_text"))
            
            # Обновляем сообщение
            try:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=keyboard.as_markup(),
                    disable_web_page_preview=False  # Разрешаем предпросмотр ссылок
                )
            except TelegramBadRequest as e:
                if "message to edit not found" in str(e).lower():
                    logger.info(f"Сообщение не найдено для редактирования: {callback.message.message_id}")
                else:
                    logger.error(f"Ошибка при редактировании сообщения: {e}")
    finally:
        # Сбрасываем флаг обработки независимо от результата
        processing_states[user_id] = False

# Обработка запроса на аудио (используется для отдельных подкатегорий)
@router.callback_query(F.data.startswith("audio_"))
async def process_audio_request(callback: CallbackQuery, state: FSMContext):
    # audio_category_subcategory
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Некорректный формат данных")
        return
    
    category = parts[1]
    subcategory = parts[2]
    
    # Пытаемся отправить аудио
    success = await send_audio(callback, category, subcategory)
    
    if not success:
        await callback.answer("Не удалось найти аудиофайл")

# Обработка запроса на демо-версию
@router.callback_query(F.data == "get_demo")
async def process_demo_request(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await callback.message.edit_text(
        text="🎁 Создадим нейросс-сотрудника вашей компании! Вы получите вызов и кастинг, и наш бот поговорит с вами лично и целостно. Для создания демо-версии нам понадобится ваш сайт.",
        reply_markup=get_main_keyboard()
    )

# Обработка возврата к главному меню
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await callback.message.edit_text(
        text=WELCOME_MESSAGE,
        reply_markup=get_main_keyboard()
    )
    
    # Очищаем состояние
    await state.clear()

# Обработка возврата к категории
@router.callback_query(F.data.startswith("back_to_category_"))
async def back_to_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Извлекаем категорию из callback_data
    category = callback.data.split("_")[3]
    
    # Возвращаемся ко второму уровню меню
    await callback.message.edit_text(
        text=CATEGORY_TEXTS.get(category, "📋 Выберите опцию:"),
        reply_markup=get_second_level_keyboard(category)
    )

# Обработка возврата к меню голосовых ботов
@router.callback_query(F.data == "back_to_voice")
async def back_to_voice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Получаем сохраненную категорию
    user_data = await state.get_data()
    category = user_data.get("current_category", "voice")
    
    # Определяем, куда возвращаться
    if category == "voice":
        await callback.message.edit_text(
            text="🎙 Выберите категорию голосового бота:",
            reply_markup=get_voice_bots_keyboard()
        )
    else:
        # Если по какой-то причине категория не voice, возвращаемся в главное меню
        await back_to_main(callback, state)

# Обработка возврата после просмотра всех аудио
@router.callback_query(F.data.startswith("back_from_audios_"))
async def back_from_audios(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Извлекаем категорию из callback_data
    category = callback.data.split("_")[3]
    
    # Удаляем все отправленные аудио
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    
    if user_id in sent_audio_messages:
        for message_id in sent_audio_messages[user_id]:
            try:
                # Удаляем сообщение напрямую
                await callback.bot.delete_message(chat_id=chat_id, message_id=message_id)
                logger.info(f"Удалено сообщение с ID {message_id}")
            except TelegramBadRequest as e:
                if "message to delete not found" in str(e).lower():
                    logger.info(f"Сообщение {message_id} уже удалено")
                else:
                    logger.error(f"Ошибка при удалении сообщения {message_id}: {e}")
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при удалении сообщения {message_id}: {e}")
        
        # Очищаем список отправленных сообщений
        del sent_audio_messages[user_id]
    
    # Получаем сохраненную категорию 
    user_data = await state.get_data()
    root_category = user_data.get("current_category", "voice")
    
    # Редактируем текущее сообщение (которое и содержит кнопку "Назад")
    if root_category == "voice":
        await callback.message.edit_text(
            text="🎙 Выберите категорию голосового бота:",
            reply_markup=get_voice_bots_keyboard()
        )
    else:
        await callback.message.edit_text(
            text=WELCOME_MESSAGE,
            reply_markup=get_main_keyboard()
        )

# Обработка возврата от аудио к категории
@router.callback_query(F.data.startswith("back_to_voice_"))
async def back_from_audio(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Извлекаем категорию из callback_data
    category = callback.data.split("_")[3]
    
    # Удаляем сообщение с аудио
    await callback.message.delete()

# Обработка возврата к меню текстовых ботов
@router.callback_query(F.data == "back_to_text")
async def back_to_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Проверяем, не обрабатывается ли уже запрос от этого пользователя
    user_id = callback.from_user.id
    if user_id in processing_states and processing_states[user_id]:
        logger.info(f"Пользователь {user_id} уже обрабатывает запрос, пропускаем")
        return
    
    # Устанавливаем флаг обработки
    processing_states[user_id] = True
    
    try:
        # Удаляем отправленные сообщения (например, PDF документы)
        chat_id = callback.message.chat.id
        
        if user_id in sent_audio_messages:
            for message_id in sent_audio_messages[user_id]:
                try:
                    # Удаляем сообщение напрямую
                    await callback.bot.delete_message(chat_id=chat_id, message_id=message_id)
                    logger.info(f"Удалено сообщение с ID {message_id}")
                except TelegramBadRequest as e:
                    if "message to delete not found" in str(e).lower():
                        logger.info(f"Сообщение {message_id} уже удалено")
                    else:
                        logger.error(f"Ошибка при удалении сообщения {message_id}: {e}")
                except Exception as e:
                    logger.error(f"Непредвиденная ошибка при удалении сообщения {message_id}: {e}")
            
            # Очищаем список отправленных сообщений
            del sent_audio_messages[user_id]
        
        # Получаем сохраненную категорию
        user_data = await state.get_data()
        category = user_data.get("current_category", "text")
        
        # Проверяем, существует ли сообщение перед редактированием
        try:
            # Возвращаемся к соответствующему меню
            if category == "text":
                await callback.message.edit_text(
                    text="💬 Выберите категорию текстового бота:",
                    reply_markup=get_text_bots_keyboard()
                )
            else:
                # Если по какой-то причине категория не text, возвращаемся в главное меню
                await back_to_main(callback, state)
        except TelegramBadRequest as e:
            if "message to edit not found" in str(e).lower():
                # Если сообщение не найдено, отправляем новое
                await callback.message.answer(
                    text="💬 Выберите категорию текстового бота:",
                    reply_markup=get_text_bots_keyboard()
                )
            else:
                logger.error(f"Ошибка при обработке возврата: {e}")
                # Попытка отправить новое сообщение в случае ошибки
                await callback.message.answer(
                    text="⚠️ Произошла ошибка. Выберите категорию текстового бота:",
                    reply_markup=get_text_bots_keyboard()
                )
    finally:
        # Сбрасываем флаг обработки независимо от результата
        processing_states[user_id] = False 

# Обработка выбора "Бесплатная демка" в текстовых ботах
@router.callback_query(F.data == "text_demo")
async def process_text_demo(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    demo_text = """Создадим для вас нейро-сотрудника вашей компании! 🔥

Наш ИИ-бот проведёт квалификацию и приведёт к целевому действию 🎯

💡 Хотите увидеть демо? 

Просто отправьте нам сайт по ссылке в ЛС 💬, и мы вышлем вам готовый результат в ближайшее время!"""
    
    # Создаем клавиатуру с кнопками "Оставить заявку" и "Назад"
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="📝 Оставить заявку", url="https://t.me/Tupikov_A"))
    keyboard.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_text"))
    
    # Обновляем сообщение
    await callback.message.edit_text(
        text=demo_text,
        reply_markup=keyboard.as_markup()
    ) 