import logging
from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext


from fsm_models import PaymentConfirmation
from models import Bill
from middlewares import AdminOnlyMiddleware


router = Router()
router.message.middleware(AdminOnlyMiddleware())


@router.message(Command('confirm_payment'), flags={'admin_only': True})
@router.message(PaymentConfirmation.uncofirmed_users, flags={'admin_only': True})
async def get_unconfirmed_users(message: types.Message, state: FSMContext):
    unconfirmed_users = await Bill.get_unpaid_by_id()
    if not unconfirmed_users:
        await message.answer('Нет неоплаченных счетов')
        return

    unconfirmed_ids = {str(i): row['bill_id'] for i, row in enumerate(unconfirmed_users, start=1)}
    message_text = Bill.get_unpaid_message_text(unconfirmed_users)
    
    await state.set_state(PaymentConfirmation.selection_confirm)
    await state.set_data(unconfirmed_ids)

    await message.answer(message_text)
    await message.answer('Для подтверждения отправьте в чат номер ')


@router.message(PaymentConfirmation.selection_confirm)
async def confirmation(message: types.Message, state: FSMContext):
    unconfirmed_ids = await state.get_data()

    if not message.text in unconfirmed_ids.keys():
        await message.answer("Это не один из предложенных счетов пользователей")
        return

    
    buttons = [
        [
            types.KeyboardButton(text="Да"),
            types.KeyboardButton(text="Нет")
        ],
    ]    
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await state.set_state(PaymentConfirmation.confirmation)
    await state.set_data({'bill_id': unconfirmed_ids[message.text]})
    await message.answer("Вы уверены?", reply_markup=keyboard)


@router.message(PaymentConfirmation.confirmation, F.text.casefold() == "нет")
async def confirmation(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(PaymentConfirmation.uncofirmed_users)
    await get_unconfirmed_users(message, state)


@router.message(PaymentConfirmation.confirmation, F.text.casefold() == "да")
async def confirmation(message: types.Message, state: FSMContext):

    data = await state.get_data()
    confirmed = await Bill.confirm_payment(data['bill_id'])
    
    if not confirmed:
        await message.answer('Что-то пошло не так, обратитесь к админам') # Emmm..., yes, thats right
        await state.clear()
        return
    
    await message.answer('Отлично, счет закрыт', reply_markup=types.ReplyKeyboardRemove())