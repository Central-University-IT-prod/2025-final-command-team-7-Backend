from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from backend.application.errors import AuthTokenNotFoundError
from bot.database.repository import Repo
from bot.keyboards.auth import auth_keyboard

start_router = Router()


@start_router.message(Command("start"))
async def message_start(message: Message, repo: Repo, state: FSMContext, command: CommandObject, bot: Bot):
    await state.clear()
    from_user = message.from_user

    user = await repo.get_user_from_tg_id(tg_id=from_user.id)
    if not user:
        try:
            user = await repo.create_user(tg_id=from_user.id, username=from_user.username)
        except Exception as e:
            await message.answer(f"Произошла ошибка при создании пользователя: {e!s}")
            return

    args = command.args
    if args and "auth_" in args:
        auth_token = str(command.args.replace("auth_", ""))

        try:
            token = await repo.get_auth_token(auth_token)

            if token and not token.activated and not token.declined:
                await message.answer(
                    f"""Подтверждение входа в систему <b>Filmhub</b>

Вы инициировали вход в Filmhub под идентификатором "<b>{from_user.full_name}</b>".

Для завершения процесса аутентификации и получения доступа к вашему аккаунту, нажмите кнопку "<b>Подтвердить вход</b>".

❗️ <i>Важно: Если вы не запрашивали доступ к системе </i>Filmhub<i> или подозреваете несанкционированную попытку входа, немедленно нажмите кнопку "Отклонить" для обеспечения безопасности вашей учетной записи.</i>""",
                    reply_markup=auth_keyboard(auth_token),
                )
            else:
                await message.answer("Этот токен авторизации уже был использован или отклонен.")

            return
        except AuthTokenNotFoundError:
            await message.answer("Ошибка: Токен авторизации не найден или устарел.")
            return

    await message.answer(
        f"Привет, {from_user.full_name}! Добро пожаловать в Filmhub Bot. "
        f"Используйте этот бот для авторизации в системе Filmhub."
    )
