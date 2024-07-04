from aiogram.fsm.state import StatesGroup, State

class UploadState(StatesGroup):
    waiting_for_notion_link = State()