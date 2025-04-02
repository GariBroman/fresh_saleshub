from aiogram import Router
from . import start, callback

# Основной роутер
router = Router()

# Регистрируем все другие роутеры
router.include_router(start.router)
router.include_router(callback.router) 