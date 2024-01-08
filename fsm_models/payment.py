from aiogram.fsm.state import State, StatesGroup


class PaymentConfirmation(StatesGroup):
    uncofirmed_users = State()
    selection_confirm = State()
    confirmation = State()