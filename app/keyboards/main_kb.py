from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Главная клавиатура с основными разделами
def get_main_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Голосовые боты", callback_data="category_voice"))
    kb.row(InlineKeyboardButton(text="Текстовые боты", callback_data="category_text"))
    kb.row(InlineKeyboardButton(text="Фото-видео боты", callback_data="category_media"))
    kb.row(InlineKeyboardButton(text="Разработка ПО", callback_data="category_dev"))
    return kb.as_markup()

# Клавиатура для второго уровня (Кейсы, Связь, Назад)
def get_second_level_keyboard(category: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Кейсы", callback_data=f"cases_{category}"))
    kb.row(InlineKeyboardButton(text="Связь", callback_data=f"contact_{category}"))
    kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    return kb.as_markup()

# Клавиатура для раздела "Голосовые боты"
def get_voice_bots_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Стоматология", callback_data="voice_dentistry"))
    kb.row(InlineKeyboardButton(text="Салоны и барбершопы", callback_data="voice_barbershop"))
    kb.row(InlineKeyboardButton(text="Клининг", callback_data="voice_cleaning"))
    kb.row(InlineKeyboardButton(text="Юриспруденция", callback_data="voice_jurisprudence"))
    kb.row(InlineKeyboardButton(text="Недвижимость", callback_data="voice_realestate"))
    kb.row(InlineKeyboardButton(text="Найм/HR", callback_data="voice_hr"))
    kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_category_voice"))
    return kb.as_markup()

# Клавиатура для раздела "Текстовые боты"
def get_text_bots_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Юридическая компания", callback_data="text_jurisprudence"))
    kb.row(InlineKeyboardButton(text="Салон красоты", callback_data="text_beauty"))
    kb.row(InlineKeyboardButton(text="Презентация бота", callback_data="text_presentation"))
    kb.row(InlineKeyboardButton(text="Видео демонстрация", callback_data="text_video"))
    kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_category_text"))
    return kb.as_markup()

# Клавиатура для кейса с ИИ-маркетологом
def get_cases_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="ИИ-маркетолог", url="https://t.me/pxinevi"))
    return kb.as_markup()

# Клавиатура для ссылок на кейсы
def get_file_keyboard(file_url: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Скачать кейс", url=file_url))
    kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_text"))
    return kb.as_markup()

# Клавиатура для бесплатной демки
def get_demo_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Получить бесплатную демку", callback_data="get_demo"))
    kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    return kb.as_markup()

# Клавиатура для связи с менеджером
def get_contact_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Связаться с менеджером", url="https://t.me/pxinevi"))
    kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    return kb.as_markup() 