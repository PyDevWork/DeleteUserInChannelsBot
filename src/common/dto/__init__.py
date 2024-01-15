from src.common.dto.question import (
    QuestionCreate,
    QuestionDTO,
    QuestionUpdate,
)
from src.common.dto.settings import (
    ComSubChatsDTO,
    ComSubChatsCreate,
    ComSubChatsUpdate,
)
from src.common.dto.user import (
    UserDTO,
    UserCreate,
    UserUpdate,
)
from src.common.dto.chat import (
    ChatDTO,
    ChatCreate,
    ChatUpdate,
)

UserDTO.model_rebuild()
QuestionDTO.model_rebuild()
ChatDTO.model_rebuild()

__all__ = (
    'UserDTO',
    'UserCreate',
    'UserUpdate',

    'QuestionCreate',
    'QuestionDTO',
    'QuestionUpdate',

    'ComSubChatsDTO',
    'ComSubChatsCreate',
    'ComSubChatsUpdate',

    'ChatDTO',
    'ChatCreate',
    'ChatUpdate'
)
