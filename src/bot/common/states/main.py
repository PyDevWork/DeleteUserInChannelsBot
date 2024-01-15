from aiogram.fsm.state import StatesGroup, State


class Support(StatesGroup):
    message = State()



class KickUser(StatesGroup):
    user_id = State()
