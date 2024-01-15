from src.database.models.user import User
from src.database.models.question import Question
from src.database.models.settings import ComSubChats
from src.database.models.chat import Chat
from src.common.dto.user import UserDTO
from src.common.dto.question import QuestionDTO
from src.common.dto.settings import ComSubChatsDTO
from src.common.dto.chat import ChatDTO


def convert_user_model_to_dto(model: User) -> UserDTO:
    questions = []
    if "questions" in model.as_dict():
        questions = [convert_question_model_to_dto(model) for model in model.questions]

    chats = []
    if "chats" in model.as_dict():
        chats = [convert_chat_model_to_dto(model) for model in model.chats]

    return UserDTO(
        user_id=model.user_id,
        first_name=model.first_name,
        last_name=model.last_name,
        language_code=model.language_code,
        is_premium=model.is_premium,
        blocked=model.blocked,
        admin=model.admin,
        questions=questions,
        chats=chats,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def convert_chat_model_to_dto(model: Chat) -> ChatDTO:
    user = None
    if "user" in model.as_dict():
        user = convert_user_model_to_dto(model.user)

    return ChatDTO(
        id=model.id,
        user_id=model.user_id,
        chat_id=model.chat_id,
        title=model.title,
        permissions=model.permissions,
        user=user,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def convert_question_model_to_dto(model: Question) -> QuestionDTO:
    user = None
    if "user" in model.as_dict():
        user = convert_user_model_to_dto(model.user)

    return QuestionDTO(
        id=model.id,
        user_message_id=model.user_message_id,
        admin_message_id=model.admin_message_id,
        status=model.status,
        user_id=model.user_id,
        user=user,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def convert_com_sub_chats_model_to_dto(model: ComSubChats) -> ComSubChatsDTO:
    return ComSubChatsDTO(
        chat_id=model.chat_id, username=model.username, turn=model.turn
    )
