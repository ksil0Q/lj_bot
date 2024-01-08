from aiogram.fsm.state import State, StatesGroup


class Advertisement(StatesGroup):
    brand = State()
    model = State()
    external_section = State()
    internal_section = State()
    selection_confirm = State()
    detail_name = State()
    image = State()
    price = State()
    description = State()
    final = State()
    # поколение?


class ClosingAdvertisement(StatesGroup):
    all_advertisemennts = State()
    closing = State()