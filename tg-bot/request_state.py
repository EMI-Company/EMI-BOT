from aiogram.fsm.state import StatesGroup, State


class RequestState(StatesGroup):
    waiting_for_request_text = State()
