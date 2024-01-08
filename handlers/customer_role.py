from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from fsm_models import CustomerRole
from models import Customer


router = Router()

@router.message(Command('become_a_customer'))
@router.message(F.text == "Хочу покупать")
async def customer(message: types.Message, state: FSMContext):
    buttons = [
        [
            types.KeyboardButton(text="Согласен"),
            types.KeyboardButton(text="Не согласен")
        ],
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
                                         resize_keyboard=True,
                                         input_field_placeholder='Подтвердите согласие'
                                         )
    
    await message.answer("""Окей, сообщение про нашу политику и все такое\nНажимая кнопку 'Согласен', вы соглашаетесь продать свою жопу в рабство""",
                         reply_markup=keyboard)
    await state.set_state(CustomerRole.confirm)
    

@router.message(CustomerRole.confirm, F.text == "Согласен")
async def confirm_role(message: types.Message, state: FSMContext):
    await Customer.get_or_create(id=message.from_user.id, username=message.from_user.username)
    await message.answer("Вам доступен личный кабинет покупателя, вызвать его можно командами:\n/my_office или /help",
                         reply_markup=types.ReplyKeyboardRemove())
    
    await message.answer('Чтобы посмотреть детали на Ваш авто, выберите из доступных - /change_my_car, а затем перейдите в меню - /menu')




#     await message.answer("Введите vin вашего авто", reply_markup=types.ReplyKeyboardRemove())
#     await state.set_state(CustomerRole.vin)


@router.message(CustomerRole.confirm, F.text == "Не согласен")
async def confirm_role(message: types.Message, state: FSMContext):
    customer_command_message = "/become_a_customer - стать покупателем"
    seller_command_message = "/become_a_seller - стать продавцом"

    message_text = '\n'.join(["Без этого не получится пользоваться площадкой\n",
                              customer_command_message, seller_command_message])
    
    await message.answer(message_text, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()



# @router.message(CustomerRole.vin)
# async def get_vin(message: types.Message, state: FSMContext):
#     message.answer("Отлично, сейчас мы попробуем найти Ваш авто", reply_markup=types.ReplyKeyboardRemove())
#     # some magic to get car number and photo
#     # ... if auto not in found: state.set_state(roles.CustomerRole.brand) return

#     buttons = [
#         [
#             types.KeyboardButton(text="Да"),
#             types.KeyboardButton(text="Нет")
#         ],
#     ]
#     keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
#                                          resize_keyboard=True,
#                                          input_field_placeholder='Ваш авто?')

#     await message.answer("Это ваш автомобиль?\n[Фото]", reply_markup=keyboard)
#     await state.set_state(CustomerRole.car_found)


# @router.message(CustomerRole.car_found, F.text == 'Да')
# async def car_found(message: types.Message, state: FSMContext):
#     await message.answer("Отлично, теперь давайте подберем деталь на ваше авто. Вызвать меню можно командой /menu",
#                          reply_markup=types.ReplyKeyboardRemove())
#     await state.set_state(DetailMenu.upper_level)


# @router.message(CustomerRole.car_found, F.text == 'Нет')
# async def car_not_found(message: types.Message, state: FSMContext):
#     await message.answer("К сожалению, мы не смогли найти Ваш авто",
#                          reply_markup=types.ReplyKeyboardRemove())
#     await state.set_state(Car.brand)
#     await brand(message, state)
