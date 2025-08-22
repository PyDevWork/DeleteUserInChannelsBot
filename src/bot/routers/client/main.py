import datetime
import random

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from src.bot import keyboards
from src.bot.common.middlewares.i18n import gettext as _
from src.bot.common.states.main import Support
from src.bot.core.models import MyBot
from src.bot.routers.client.router import client_router
from src.bot.utils.callback import CallbackData as Cb
from src.bot.utils.texts import client as texts
from src.common.dto import QuestionCreate
from src.common.dto.chat import ChatUpdate
from src.config.settings import Settings
from src.database.core import Database
from aiogram.exceptions import TelegramRetryAfter
import asyncio
MAX_MESSAGE_LENGTH = 4096  # Лимит Telegram


def split_message(text: str):
    """
    Разбивает текст на части, не превышающие 4096 символов.
    """
    parts = [
        text[i : i + MAX_MESSAGE_LENGTH]
        for i in range(0, len(text), MAX_MESSAGE_LENGTH)
    ]
    return parts


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
async def start_cq(callback: types.CallbackQuery, db: Database):
    data = Cb.extract(callback.data)

    if data.data == Cb.Start.channel_list():
        all_chats = await db.chat.select_many()
        chats_admin = [
            i for i in all_chats if i.permissions["status"] == "administrator"
        ]

        text = ""

        for i in chats_admin:
            text += f"{i.title} | {i.chat_id}\n"

        if text == "":
            text = "Пусто"

        for i in split_message(text):
            await callback.message.reply(i)


@client_router.message(Command("kick"))
async def get_user_id_kick(message: types.Message, bot: MyBot, db: Database):
    try:
        user_id = int(message.text.split(" ")[1])
    except ValueError:
        reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
        await message.reply(
            _(texts.KICK_USER_ID_MUST_BE_INTEGER), reply_markup=reply_markup
        )
        return

    except IndexError:
        reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
        await message.reply(
            "После комманды вы должны указать ID пользователя",
            reply_markup=reply_markup,
        )
        return

    all_chats = await db.chat.select_many()
    chats_admin = [i for i in all_chats if i.permissions["status"] == "administrator"]

    reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
    mes = await message.answer(
        text=_(texts.KICK_PROCESS_STARTED).format(len(chats_admin)),
        reply_markup=reply_markup,
    )

    success = []
    errors = []

    for i in chats_admin:
        try:
            res = await bot.get_chat_member(chat_id=i.chat_id, user_id=user_id)
            if res.status.name == "LEFT":
                errors.append((i.title, i.chat_id))
                continue
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

    txt = _(texts.KICK_PROCESS_FINISH).format(text)

    for i in split_message(txt):
        await mes.answer(
            text=i, reply_markup=reply_markup
        )


@client_router.message(Command("user"))
async def get_user_id_chats(message: types.Message, bot: MyBot, db: Database):
    try:
        user_id = int(message.text.split(" ")[1])
    except ValueError:
        reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
        await message.reply(
            _(texts.USER_USER_ID_MUST_BE_INTEGER), reply_markup=reply_markup
        )
        return

    except IndexError:
        reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
        await message.reply(
            "После комманды вы должны указать ID пользователя",
            reply_markup=reply_markup,
        )
        return

    all_chats = await db.chat.select_many()
    chats_admin = [i for i in all_chats if i.permissions["status"] == "administrator"]

    reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
    mes = await message.answer(
        text=_(texts.KICK_PROCESS_STARTED).format(len(chats_admin)),
        reply_markup=reply_markup,
    )

    text = ""

    for i in chats_admin:
        try:
            res = await bot.get_chat_member(chat_id=i.chat_id, user_id=user_id)
            res.status.name
            smile = ""
            if res.status.name == "LEFT":
                smile = "🚾"
            elif res.status.name == "KICKED":
                smile = "❌"
            elif res.status.name == "MEMBER":
                smile = "✅"
            text += f"{smile} | {res.status.name} - {i.title} | {i.chat_id}\n"
        except TelegramBadRequest:
            text += f"🚫 - {i.title} | {i.chat_id}\n"

    txt = _(texts.USER_PROCESS_FINISH).format(text)
    for i in split_message(txt):
        await mes.answer(
            text=i, reply_markup=reply_markup
        )


@client_router.message(Command("chat_links"))
async def get_expired_data_chat_links(message: types.Message, bot: MyBot, db: Database):
    try:
        expired_data = int(message.text.split(" ")[1])
    except ValueError:
        reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
        await message.reply(
            "Ошибка, дни должны быть указаны как число", reply_markup=reply_markup
        )
        return

    except IndexError:
        reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)
        await message.reply(
            "После комманды вы должны количетсво часов действия ссылок",
            reply_markup=reply_markup,
        )
        return

    all_chats = await db.chat.select_many()
    chats_admin = [i for i in all_chats if i.permissions["status"] == "administrator"]

    text = ""

    for i in chats_admin:
        try:
            res = await bot.create_chat_invite_link(
                chat_id=i.chat_id,
                expire_date=datetime.timedelta(hours=expired_data),
                member_limit=1,
            )
            text += f"{i.title} | {i.chat_id} -> {res.invite_link}\n"
        except TelegramBadRequest:
            text += f"🚫 - {i.title} | {i.chat_id}\n"

    reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)

    txt = _(texts.CHAT_LINK_PROCESS_FINISH).format(text)
    for i in split_message(txt):
        await message.answer(
            text=i, reply_markup=reply_markup
        )

async def get_chat(bot, chat_id):
    try:
        return await bot.get_chat(chat_id=chat_id)
    except TelegramRetryAfter as e:
        print(f"Превышен лимит. Ждём {e.timeout} секунд")
        await asyncio.sleep(e.timeout + 1)
        return await bot.get_chat(chat_id=chat_id)

async def get_chat_member_count(bot, chat_id):
    try:
        return await bot.get_chat_member_count(chat_id=chat_id)
    except TelegramRetryAfter as e:
        print(f"Превышен лимит. Ждём {e.timeout} секунд")
        await asyncio.sleep(e.timeout + 1)
        return await bot.get_chat_member_count(chat_id=chat_id)

@client_router.message(Command("renew"))
async def renew(message: types.Message, bot: MyBot, db: Database):
    all_chats = await db.chat.select_many()
    chats_admin = [i for i in all_chats if i.permissions["status"] == "administrator"]

    reply_markup = keyboards.back(to=Cb.Back.main_menu(), main_menu=True)

    mes = await message.answer(
        text=_(texts.RENEW_PROCESS_STARTED).format(len(chats_admin)),
        reply_markup=reply_markup,
    )
    success = []
    errors = []
    not_edited = []

    for i in chats_admin:
        try:
            res = await get_chat(bot, chat_id=i.chat_id)
            if res.title == i.title:
                not_edited.append((i.title, i.chat_id))
                continue
            else:
                await db.chat.update(
                    chat_id=i.chat_id,
                    query=ChatUpdate(title=res.title),
                )
                success.append((i.title, i.chat_id, res.title))
        except TelegramBadRequest:
            errors.append((i.title, i.chat_id))

    text = ""

    for i in success:
        text += f"✅ - {i[0]} -> {i[2]} | {i[1]}\n"
    for i in not_edited:
        text += f"🗿 - {i[0]} | {i[1]}\n"
    for i in errors:
        text += f"🚫 - {i[0]} | {i[1]}\n"

    txt = _(texts.RENEW_PROCESS_FINISH).format(text)

    for i in split_message(txt):
        await mes.answer(text=i, reply_markup=reply_markup)

    chats_member = ""
    for i in chats_admin:
        try:
            res = await get_chat_member_count(bot, chat_id=i.chat_id)
            chats_member += f"{i.title}: {res}"
        except TelegramBadRequest:
            ...

    with open("log.txt", "w") as f:
        f.write(chats_member)


@client_router.callback_query(lambda c: Cb.extract(c.data, True).data == Cb.Back())
async def back(callback: types.CallbackQuery, state: FSMContext):
    data = Cb.extract(callback.data)
    if data.data == Cb.Back.main_menu():
        await state.clear()
        await callback.message.delete()

        reply_markup = keyboards.start()

        await callback.message.answer(_(texts.START), reply_markup=reply_markup)
