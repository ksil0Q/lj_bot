from aiogram.fsm.state import State, StatesGroup


class Car(StatesGroup):
    brand = State()
    model = State()
    selection_confirm = State()
    final = State()
    # поколение?
