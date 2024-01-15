from src.database.repositories.user import UserRepository
from src.database.repositories.question import QuestionRepository
from src.database.repositories.settings import ComSubChatsRepository
from src.database.repositories.chat import ChatRepository

__all__ = (
    'UserRepository',
    'QuestionRepository',
    'ComSubChatsRepository',
    'ChatRepository',
)

REPOSITORIES = (
    UserRepository,
    QuestionRepository,
    ComSubChatsRepository,
    ChatRepository,
)
