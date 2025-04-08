import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (если он существует)
load_dotenv()

# Токен бота из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Проверка наличия токена
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не настроен. Укажите его в переменных окружения или .env файле")

# Базовый путь к проекту
BASE_DIR = Path(__file__).parent.parent

# Путь к аудиофайлам
SOUNDS_DIR = BASE_DIR / "sounds"

# Категории из схемы
CATEGORIES = {
    "dentistry": "Стоматология",
    "barbershop": "Салоны и барбершопы",
    "cleaning": "Клининг",
    "jurisprudence": "Юриспруденция",
    "realestate": "Недвижимость",
    "hr": "Найм/HR"
}

# Контакт для перенаправления из переменной окружения или дефолтный
MARKETING_CONTACT = os.getenv("MARKETING_CONTACT", "@maximdeveloper") 