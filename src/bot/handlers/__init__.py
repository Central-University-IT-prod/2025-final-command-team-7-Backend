from aiogram import Dispatcher, F

from .auth import auth_router
from .start import start_router


def setup_routers(dispatcher: Dispatcher):
    start_router.message.filter(F.chat.type == "private")
    dispatcher.include_router(start_router)
    dispatcher.include_router(auth_router)
