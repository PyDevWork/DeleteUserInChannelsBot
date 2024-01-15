from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from src.common.dto.user import UserDTO


class ChatCreate(BaseModel):
    user_id: int
    chat_id: int
    title: str
    permissions: dict


class ChatUpdate(BaseModel):
    title: Optional[str] = None
    permissions: Optional[dict] = None


class ChatDTO(BaseModel):
    id: int
    user_id: int
    chat_id: int
    title: str
    permissions: dict

    user: Optional["UserDTO"]

    created_at: datetime
    updated_at: datetime
