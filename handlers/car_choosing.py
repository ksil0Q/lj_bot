from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import logging


from fsm_models import Car
from models import Brand, Model, Customer
from middlewares import CustomerOnlyMiddleware
from loader import max_brands_in_row, max_models_in_row, psql_manager
from handlers.common import my_office


router = Router()
router.message.middleware(CustomerOnlyMiddleware())


@router.message(Command("change_my_car"), flags={'customer_only': True})
@router.message(Car.brand, flags={'customer_only': True})
async def brand(message: types.Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()

    buttons = []
    brand_fields = await Brand.get_fields_of_popular_brands('id', 'brand_name')

    for i, brand in enumerate(brand_fields, 1):
        buttons.append(types.KeyboardButton(text=brand['brand_name']))
        if i % max_brands_in_row == 0:
            builder.row(*buttons)
            buttons.clear()

    if buttons:
        builder.row(*buttons)

    builder.row(types.KeyboardButton(text="Отмена"))

    await message.answer("Давайте выберем марку Вашего авто",
                         reply_markup=builder.as_markup(resize_keyboard=True,
                                                        input_field_placeholder='Выберите модель'))
    await state.set_state(Car.model)
    await state.set_data(brand_fields)


@router.message(Car.model, F.text.casefold() == "отмена")
async def back_button(message: types.Message, state: FSMContext):
    await state.set_data({}) # clear state data
    await state.clear()
    await my_office(message)


@router.message(Car.model)
async def model(message: types.Message, state: FSMContext):
    brand_fields = await state.get_data()

    try:
        brand_id = next(filter(lambda brand: brand['brand_name'] == message.text, brand_fields))['id']
    except StopIteration:
        await message.answer("К сожалению, мы не знаем о такой марки, пожалуйста, выберите из предложенных")
        return
    
    model_names = await Model.get_names(brand_id)

    builder = ReplyKeyboardBuilder()
    buttons = []
    for i, name in enumerate(model_names, start=1):
        buttons.append(types.KeyboardButton(text=name))
        if i % max_models_in_row == 0:
            builder.row(*buttons)
            buttons.clear()

    if buttons:
        builder.row(*buttons)

    builder.row(types.KeyboardButton(text="Назад"))
    
    await message.answer("Давайте выберем модель Вашего авто",
                         reply_markup=builder.as_markup(
                            resize_keyboard=True,
                            input_field_placeholder="Выберите модель"
    ))
    
    await state.set_state(Car.selection_confirm)
    await state.set_data({'id': brand_id, 'brand_name': message.text})


@router.message(Car.model)
async def incorrect_brand(message: types.Message, state: FSMContext): 
    await message.answer('Я не знаю такого производителя, выберите из предложенных вариантов')


@router.message(Car.selection_confirm, F.text.casefold() == "назад")
async def back_button(message: types.Message, state: FSMContext):
    await state.set_data({}) # clear state data
    await state.set_state(Car.brand)
    await brand(message, state)


@router.message(Car.selection_confirm)
async def final(message: types.Message, state: FSMContext):
    brand_fields = await state.get_data()
    model_names = await Model.get_names(brand_fields['id'])

    if message.text not in model_names:
        await message.answer(f'Я не знаю такой модели у {brand_fields["brand_name"]}, пожалуйста, выберите из предложенных')
        return

    model_id = await psql_manager.get(Model, model_name=message.text, brand_id=brand_fields['id'])
    saved = await Customer.save_car(message.from_user.id, brand_fields['id'], model_id)

    if not saved:
        await message.answer("Что-то пошло не так обратитесь к админам", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return 
    
    await message.answer("Отлично! Команда /menu для перехода в меню\nЧтобы поменять авто можно воспользоваться командой:\n/change_my_car",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
