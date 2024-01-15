import random

from aiogram import F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from src.bot import keyboards
from src.bot.core.models import MyBot
from src.config.settings import Settings
from src.bot.utils.texts import client as texts
from src.database.core import Database
from src.common.dto import QuestionCreate
from src.bot.common.states.main import Support, KickUser

from src.bot.utils.callback import CallbackData as Cb
from src.bot.routers.client.router import client_router
from src.bot.common.middlewares.i18n import gettext as _


@client_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text=_(texts.START), reply_markup=keyboards.start())


@client_router.message(Command("support"))
async def support(message: types.Message, state: FSMContext):
    await state.set_state(Support.message)
    await message.reply(
        text=_(texts.SUPPORT),
        reply_markup=keyboards.back(to=Cb.Back.main_menu(), main_menu=True),
    )


@client_router.message(Support.message)
async def get_support_message(
    message: types.Message, state: FSMContext, settings: Settings, db: Database
):
    await state.clear()

    db_admins = [user.user_id for user in await db.user.get_admins()]
    admins = db_admins + settings.admins

    if not admins:
        await message.reply(_(texts.ADMINS_NOT_FOUND))
        return

    mes = await message.forward(chat_id=random.choice(admins))
    await db.question.create(
        query=QuestionCreate(
            user_id=message.from_user.id,
            user_message_id=message.message_id,
            admin_message_id=mes.message_id,
        )
    )
    await message.reply(_(texts.SUPPORT_YOUR_MESSAGE_SEND_ADMIN))


@client_router.callback_query(lambda c: Cb.extract(c.data, True).data == Cb.Start())
async def back(callback: types.CallbackQuery, state: FSMContext, db: Database):
    data = Cb.extract(callback.data)
    if data.data == Cb.Start.kick():
        await callback.message.delete()
        reply_markup = keyboards.back(to=Cb.Back.main_menu(), cancel=True)
        await callback.message.answer(
            _(texts.SEND_USER_ID_FOR_KICK), reply_markup=reply_markup
        )
        await state.set_state(KickUser.user_id)

    elif data.data == Cb.Start.channel_list():
        all_chats = await db.chat.select_many()
        chats_admin = [
            i for i in all_chats if i.permissions["status"] == "administrator"
        ]

        text = ""

        for i in chats_admin:
            text += f"{i.title} | {i.chat_id}\n"

        if text == '':
            text = 'Пусто'

        await callback.message.reply(text)


@client_router.message(F.text, KickUser.user_id)
async def get_user_id_kick(
    message: types.Message, bot: MyBot, state: FSMContext, db: Database
):
    try:
        user_id = int(message.text)
    except ValueError:
        reply_markup = keyboards.back(to=Cb.Back.main_menu(), cancel=True)
        await message.reply(
            _(texts.KICK_USER_ID_MUST_BE_INTEGER), reply_markup=reply_markup
        )
        return

    all_chats = await db.chat.select_many()
    chats_admin = [i for i in all_chats if i.permissions["status"] == "administrator"]

    reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
    mes = await message.answer(
        text=_(texts.KICK_PROCESS_STARTED).format(len(chats_admin)),
        reply_markup=reply_markup,
    )
    await state.clear()

    success = []
    errors = []

    for i in chats_admin:
        try:
            await bot.ban_chat_member(chat_id=i.chat_id, user_id=user_id)
            await bot.unban_chat_member(
                chat_id=i.chat_id, user_id=user_id, only_if_banned=True
            )
            success.append((i.title, i.chat_id))
        except TelegramBadRequest:
            errors.append((i.title, i.chat_id))

    text = ""

    for i in success:
        text += f"✅ - {i[0]} | {i[1]}\n"
    for i in errors:
        text += f"🚫 - {i[0]} | {i[1]}\n"

    await mes.answer(
        text=_(texts.KICK_PROCESS_FINISH).format(text), reply_markup=reply_markup
    )


@client_router.callback_query(lambda c: Cb.extract(c.data, True).data == Cb.Back())
async def back(callback: types.CallbackQuery, state: FSMContext):
    data = Cb.extract(callback.data)
    if data.data == Cb.Back.main_menu():
        await state.clear()
        await callback.message.delete()

        reply_markup = keyboards.start()

        await callback.message.answer(_(texts.START), reply_markup=reply_markup)
