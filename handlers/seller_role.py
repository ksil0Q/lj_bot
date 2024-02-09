from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime, timedelta
import logging


from fsm_models import SellerRole
from models import Admin, Tariff, Customer, Bill, Seller
from loader import max_tariffs_in_row


router = Router()


@router.message(F.text == "Хочу продавать")
async def seller(message: types.Message, state: FSMContext):
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
    await state.set_state(SellerRole.confirm)


@router.message(Command(commands=["become_a_seller", "choose_a_tariff"]))
@router.message(SellerRole.confirm, F.text.casefold() == "согласен")
async def confirm_role(message: types.Message, state: FSMContext):
    tariffs = await Tariff.get_values()
    
    builder = ReplyKeyboardBuilder()
    buttons = []

    for i, tariff in enumerate(tariffs, start=1):
        buttons.append(types.KeyboardButton(text=tariff['tariff_name']))
        if i % max_tariffs_in_row == 0:
            builder.row(*buttons)
            buttons.clear()
    
    if buttons:
        builder.row(*buttons)

    builder.row(types.KeyboardButton(text='Отмена'))
    formatted_tariffs = Tariff.format_for_message(tariffs)

    await message.answer(f"Для получения доступа к продаже автозапчастей на нашей площадке, нужно сделать следующее:\r\
                         выбрать тариф, оплатить по указанным реквизитам, прикрепив кодик в сообщении об оплате.\nТарифы:\
                         \n{formatted_tariffs}\n\n[Реквизиты для оплаты]", reply_markup=builder.as_markup(resize_keyboard=True))
    
    await state.set_state(SellerRole.payment_confirm)


@router.message(SellerRole.confirm, F.text.casefold() == "не согласен")
async def not_confirm_role(message: types.Message, state: FSMContext):
    customer_command_message = "/become_a_customer - стать покупателем"
    seller_command_message = "/become_a_seller - стать продавцом"

    message_text = '\n'.join(["Без этого не получится пользоваться площадкой\n",
                              seller_command_message, customer_command_message])
    
    await message.answer(message_text,
                         reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@router.message(SellerRole.payment_confirm, F.text.casefold() == 'отмена')
async def back_button(message: types.Message, state: FSMContext):
    await state.set_data({})
    await state.set_state(SellerRole.confirm)
    await confirm_role(message, state)


@router.message(SellerRole.payment_confirm)
async def payment_agree(message: types.Message, state: FSMContext):
    tariff_id = await Tariff.get_id_by_name(message.text)

    if not tariff_id:
        await message.answer("К сожалению, нет такого тарифа, пожалуйста, выберите из предложенных")
        return
    
    seller = await Seller.get_or_create(id=message.from_user.id,
                                                 username=message.from_user.username)
    
    await Customer.get_or_create(id=message.from_user.id,
                                     username=message.from_user.username)
    
    expiration_date = datetime.now() + timedelta(days=1)
    bill = await Bill.create_or_update(user_id=seller.id, tariff_id=tariff_id,
                                 closed=False, creation_date=datetime.now(),
                                 expiration_date=expiration_date)
    
    code = await bill.get_code(bill.id)

    buttons = [
        [
            types.KeyboardButton(text="Оплатил"),
            types.KeyboardButton(text="Отмена")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
                                         resize_keyboard=True)

    await message.answer(f"Ваш кодик {code}, не забудьте прикрепить его в сообщении оплаты. "
                         "На оплату даются 1 сутки. После оплаты нажмите 'Оплатил'", reply_markup=keyboard)
    
    await state.set_state(SellerRole.end_state)


@router.message(SellerRole.end_state, F.text.casefold() == 'оплатил')
async def tariff_paid(message: types.Message, state: FSMContext):
    admin_usernames = await Admin.get_usernames()
    converted_usernames = ", ".join([f'@{name}' for name in admin_usernames])
    await message.answer("Отлично, в течение двух суток администрация подтвердит оплату и Вам будет доступна возможность выкладывать объявления. "
                         f"По всем вопросам писать {converted_usernames}",
                         reply_markup=types.ReplyKeyboardRemove())
    
    await message.answer("Вам доступен личный кабинет, перейти в него можно с помощью:\n/my_office или /help")
    

@router.message(SellerRole.end_state, F.text.casefold() == 'отмена')
async def back_button(message: types.Message, state: FSMContext):
    await state.set_data({})
    await state.set_state(SellerRole.confirm)
    await confirm_role(message, state)