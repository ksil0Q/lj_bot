from aiogram.fsm.state import State, StatesGroup


class DetailMenu(StatesGroup):
    upper_level = State()
    lower_level = State()
    selection_confirm = State()
    final = State()
    inline_mode = State()
