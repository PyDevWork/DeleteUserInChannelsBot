from typing import (
    Optional,
    Type,
    List,
)

from src.database.converters import convert_chat_model_to_dto
from src.common.dto import (
    ChatCreate,
    ChatDTO,
    ChatUpdate,
)
from src.database.interfaces.repositories.base import Repository
from src.database.models.chat import Chat
from src.database.repositories.base import BaseRepository


class ChatRepository(
    BaseRepository[Chat], Repository[int, ChatDTO, ChatCreate, ChatUpdate]
):
    model: Type[Chat] = Chat

    async def create(self, query: ChatCreate) -> Optional[ChatDTO]:
        result = await self._crud.create(**query.model_dump(exclude_none=True))
        if not result:
            return None

        return convert_chat_model_to_dto(result)

    async def select(self, chat_id: int) -> Optional[ChatDTO]:
        result = await self._crud.select(self.model.chat_id == chat_id)
        if not result:
            return None

        return convert_chat_model_to_dto(result)

    async def select_many(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[ChatDTO]:
        result = await self._crud.select_many(offset=offset, limit=limit)
        return [convert_chat_model_to_dto(model) for model in result]

    async def update(
        self, chat_id: int, query: ChatUpdate, exclude_none: bool = True
    ) -> List[ChatDTO]:
        result = await self._crud.update(
            self.model.chat_id == chat_id, **query.model_dump(exclude_none=exclude_none)
        )
        return [convert_chat_model_to_dto(model) for model in result]

    async def delete(self, chat_id: int) -> List[ChatDTO]:
        result = await self._crud.delete(self.model.chat_id == chat_id)
        return [convert_chat_model_to_dto(model) for model in result]
