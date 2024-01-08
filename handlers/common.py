from aiogram import Router, types, F
from aiogram.filters import Command


import logging
from models import Customer, Admin, Customer


router = Router()

# TODO: seller could skip some steps of advertisement creating
@router.message(Command('start'))
async def start(message: types.Message):
    buttons = [
        [
            types.KeyboardButton(text='Хочу продавать'),
            types.KeyboardButton(text='Хочу покупать')
        ],
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
                                               resize_keyboard=True,
                                               input_field_placeholder="Выберите роль")
    
    await message.answer("Приветственное сообщение с предупреждениями и предложение выбрать роль...",
                         reply_markup=keyboard)


@router.message(Command(commands=['my_office', 'help']))
async def my_office(message: types.Message):
    admin = await Admin.get_or_none(id=message.from_user.id)

    if admin:
        admin_commands = "\n".join(Admin.commands)
        await message.answer(f'Добро пожаловать в личный кабинет, доступные команды:\n{admin_commands}',
                             
                             reply_markup=types.ReplyKeyboardRemove())
        return
    
    seller = await Customer.get_or_none(id=message.from_user.id)

    if seller:
        seller_commands = "\n".join(Customer.commands)
        await message.answer(f'Добро пожаловать в личный кабинет, доступные команды:\n{seller_commands}',
                             reply_markup=types.ReplyKeyboardRemove())
        return 

    customer = await Customer.get_or_none(id=message.from_user.id)

    if customer:
        customer_commands = '\n'.join(Customer.commands)
        await message.answer(f'Добро пожаловать в личный кабинет, доступные команды:\n{customer_commands}',
                             reply_markup=types.ReplyKeyboardRemove())
        return
    
    await message.answer('Для использования воспользуйтесь командой /start')

    # TODO find places where i need to add a "reply_markup=types.ReplyKeyboardRemove(resize_keyboard=True)"

@router.message()
async def answer_to_other_messages(message: types.Message):
    user_id = message.from_user.id

    user = await Customer.get_or_none(id=user_id)

    if not user:
        await message.answer('Для пользования площадкой - /start')
        return
    
    await message.answer('Попробуйте /my_office или /help')