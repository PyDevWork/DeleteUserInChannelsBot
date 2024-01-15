from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, ModelWithID, ModelWithTime


if TYPE_CHECKING:
    from src.database.models.user import User


class Chat(Base, ModelWithID, ModelWithTime):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    chat_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str]
    permissions: Mapped[dict] = mapped_column(JSON)

    user: Mapped["User"] = relationship("User", back_populates="chats")
