from src.bot.routers.channel.router import channel_router
from src.bot.common.middlewares.i18n import gettext as _

from aiogram.types.chat_member_updated import ChatMemberUpdated
from src.common.dto.chat import ChatCreate, ChatUpdate

from src.database.core.database import Database


@channel_router.my_chat_member()
async def start(update: ChatMemberUpdated, db: Database):
    permissions = update.new_chat_member.model_dump(exclude="user", mode='json')
    db_chat_info = await db.chat.select(chat_id=update.chat.id)
    if db_chat_info is None:
        await db.chat.create(query=ChatCreate(
            user_id=update.from_user.id,
            chat_id=update.chat.id,
            title=update.chat.title,
            permissions=permissions
        ))
        return
    await db.chat.update(chat_id=db_chat_info.chat_id, query=ChatUpdate(
        permissions=permissions
    ))
