from aiogram.fsm.state import State, StatesGroup


class CustomerRole(StatesGroup):
    confirm = State()
    vin = State()
    car_found = State()


class SellerRole(StatesGroup):
    confirm = State()
    payment = State()
    payment_confirm = State()
    end_state = State()