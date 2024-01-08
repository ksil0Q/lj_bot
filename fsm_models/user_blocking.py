from aiogram.fsm.state import State, StatesGroup


class UserBlocking(StatesGroup):
    username_asking = State()
    add_a_reason = State()
    selection_confirm = State()


class UserUnBlocking(StatesGroup):
    username_asking = State()
    selection_confirm = State()