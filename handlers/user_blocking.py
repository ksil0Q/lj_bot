from aiogram.filters import Command
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
import logging


from fsm_models import UserBlocking, UserUnBlocking
from models import Customer
from middlewares import AdminOnlyMiddleware


router = Router()
router.message.middleware(AdminOnlyMiddleware())


@router.message(Command("block_a_user"), flags={'admin_only': True})
@router.message(UserBlocking.username_asking, flags={'admin_only': True})
async def blocking(message: types.Message, state: FSMContext):
    await message.answer("Отправьте username пользователя")
    await state.set_state(UserBlocking.add_a_reason)


@router.message(UserBlocking.add_a_reason)
async def add_a_reason(message: types.Message, state: FSMContext):
    username = message.text.removeprefix('@')
    customer = await Customer.get_or_none(username=username)

    if not customer:
        await message.answer("Нет пользователя с таким именем")
        return
    
    await message.answer('Укажите причину')
    await state.set_data([customer.id, username])
    await state.set_state(UserBlocking.selection_confirm)


@router.message(UserBlocking.selection_confirm)
async def selection_confirm(message: types.Message, state: FSMContext):
    customer_id, username = await state.get_data()
    logging.info(customer_id)

    blocked = await Customer.block_user(customer_id, message.text)

    if blocked:
        await message.answer(f"Пользователь @{username} заблокирован")
    else:
        await message.answer("Что-то пошло не так")

    await state.clear()



@router.message(Command("unblock_a_user"))
@router.message(UserUnBlocking.username_asking)
async def unblocking(message: types.Message, state: FSMContext):
    await message.answer("Отправьте username пользователя")
    await state.set_state(UserUnBlocking.selection_confirm)


@router.message(UserUnBlocking.selection_confirm)
async def selection_confirm(message: types.Message, state: FSMContext):
    username = message.text.removeprefix('@')
    customer = await Customer.get_or_none(username=username)

    if not customer:
        await message.answer("Нет пользователя с таким именем")
        return
    
    unblocked = await Customer.unblock_user(customer.id)

    if unblocked:
        await message.answer(f"Пользователь @{username} разблокирован")
    else:
        await message.answer("Что-то пошло не так")

    await state.clear()