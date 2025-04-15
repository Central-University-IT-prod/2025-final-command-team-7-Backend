import uuid
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from backend.application.errors import AuthTokenNotFoundError
from backend.domain.watchlist_type import WatchlistType
from backend.infrastructure.persistence.models.watchlist import WatchlistORM
from bot.database.repository import Repo
from bot.keyboards.auth import ConfirmAuthCallbackData, DeclineAuthCallbackData

auth_router = Router()


@auth_router.callback_query(ConfirmAuthCallbackData.filter())
async def callback_auth_confirm(
    callback: CallbackQuery, callback_data: ConfirmAuthCallbackData, repo: Repo, state: FSMContext
):
    await callback.answer()
    token_str = callback_data.auth_token

    try:
        user = await repo.get_user_from_tg_id(tg_id=callback.from_user.id)
        if not user:
            user = await repo.create_user(tg_id=callback.from_user.id, username=callback.from_user.username)

            watchlists = (
                WatchlistORM(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    title="Мои любимые",
                    type=WatchlistType.liked,
                    color1="#FF36AB",
                    color2="#FF74D4",
                    color3="#ED5C86",
                ),
                WatchlistORM(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    title="Просмотренные",
                    type=WatchlistType.watched,
                    color1="#31B4EA",
                    color2="#6F97EB",
                    color3="#B577EC",
                ),
                WatchlistORM(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    title="Хочу посмотреть",
                    type=WatchlistType.wish,
                    color1="#EE0979",
                    color2="#FF6A00",
                    color3="#FFF647",
                ),
            )
            repo.session.add_all(watchlists)
            await repo.session.commit()

        token = await repo.get_auth_token(token_str)

        if token and not token.activated and not token.declined:
            await repo.activate_auth_token(token_str, user.id)

            await callback.message.edit_text(
                f"""Вход в систему Filmhub под идентификатором "{callback.from_user.full_name}" подтвержден. """
                f"""Можете продолжить работу с сайтом."""
            )
        else:
            await callback.message.edit_text("Токен авторизации уже был использован или отклонен.")

    except AuthTokenNotFoundError:
        await callback.message.edit_text("Ошибка: Токен авторизации не найден или устарел.")
    except Exception as e:
        await callback.message.edit_text(f"Произошла ошибка при подтверждении входа: {e!s}")

    await state.clear()


@auth_router.callback_query(DeclineAuthCallbackData.filter())
async def callback_auth_decline(
    callback: CallbackQuery, callback_data: DeclineAuthCallbackData, repo: Repo, state: FSMContext
):
    await callback.answer()
    token_str = callback_data.auth_token

    try:
        token = await repo.get_auth_token(token_str)

        if token and not token.activated and not token.declined:
            await repo.decline_auth_token(token_str)
            await callback.message.edit_text("Вход в систему отменён.")
        else:
            await callback.message.edit_text("Токен авторизации уже был использован или отклонен.")

    except AuthTokenNotFoundError:
        await callback.message.edit_text("Ошибка: Токен авторизации не найден или устарел.")
    except Exception as e:
        await callback.message.edit_text(f"Произошла ошибка при отклонении входа: {e!s}")

    await state.clear()
