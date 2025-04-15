from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ConfirmAuthCallbackData(CallbackData, prefix="/auth/confirm"):
    auth_token: str


class DeclineAuthCallbackData(CallbackData, prefix="/auth/decline"):
    auth_token: str


def auth_keyboard(auth_token) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Подтвердить вход", callback_data=ConfirmAuthCallbackData(auth_token=auth_token).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(text="Отклонить", callback_data=DeclineAuthCallbackData(auth_token=auth_token).pack())
    )
    return builder.as_markup()
