import logging
from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from fsm_models import Advertisement
from handlers.common import my_office
from middlewares import SellerOnlyMiddleware
from models import Brand, Model, Seller, ExternalMenu, InternalMenu, Detail
from loader import max_brands_in_row, max_models_in_row,\
                    max_detail_menu_sections_in_row


router = Router()
router.message.middleware(SellerOnlyMiddleware())


@router.message(Command('create_advertisement'), flags={'seller_only': True})
@router.message(Advertisement.brand, flags={'seller_only': True})
async def access_check(message: types.Message, state: FSMContext):

    seller = await Seller.get_or_none(Seller.id==message.from_user.id)

    if not seller.available_advertisements:
        await message.answer(f"Количество доступных объявлений для публикации: {seller.available_advertisements}\nПополните баланс /choose_a_tariff",
                             reply_markup=types.ReplyKeyboardRemove())
        return

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

    await state.set_state(Advertisement.model)
    data = {'available_advertisements': seller.available_advertisements, 'brand_fields': brand_fields}
    await state.set_data(data)

    await message.answer("Давайте выберем марку авто, которому подходит деталь",
                         reply_markup=builder.as_markup(resize_keyboard=True,
                                                        input_field_placeholder='Выберите модель'))


@router.message(Advertisement.model, F.text.casefold() == 'отмена')
async def back_button(message: types.Message, state: FSMContext):
    await state.set_data({}) # clear state data
    await state.clear()
    await my_office(message)


@router.message(Advertisement.model)
async def model(message: types.Message, state: FSMContext):

    data = await state.get_data()
    brand_fields = data['brand_fields']

    brand_name = data.get('brand_name', message.text)

    try:
        brand_id = next(filter(lambda brand: brand['brand_name'] == brand_name, brand_fields))['id']
    except StopIteration:
        await message.answer("К сожалению, мы не знаем о такой модели, пожалуйста, выберите из предложенных")
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
    
    await message.answer("Теперь модель",
                         reply_markup=builder.as_markup(
                            resize_keyboard=True,
                            input_field_placeholder="Выберите модель"
    ))
    await state.set_state(Advertisement.external_section)
    data.update({'brand_id': brand_id, 'brand_name': brand_name})
    await state.set_data(data)


@router.message(Advertisement.model)
async def incorrect_brand(message: types.Message, state: FSMContext): 
    await message.answer('Я не знаю такого производителя, выберите из предложенных вариантов')


@router.message(Advertisement.external_section, F.text.casefold() == "назад")
async def back_button(message: types.Message, state: FSMContext):
    await state.set_data({}) # clear state data
    await state.set_state(Advertisement.brand)
    await access_check(message, state)


@router.message(Advertisement.external_section)
async def external_section(message: types.Message, state: FSMContext):
    data = await state.get_data()
    model_names = await Model.get_names(data['brand_id'])
    model_name = data.get('model_name', message.text)
    if model_name not in model_names:
        await message.answer(f'Я не знаю такой модели у {data["brand_name"]}, пожалуйста, выберите из предложенных')
        return
    
    external_sections = await ExternalMenu.get_sections()

    builder = ReplyKeyboardBuilder()
    buttons = []

    for i, section in enumerate(external_sections, start=1):
        buttons.append(types.KeyboardButton(text=section.section_name))
        if i % max_detail_menu_sections_in_row == 0:
            builder.row(*buttons)
            buttons.clear()

    if buttons:
        builder.row(*buttons)
    
    builder.row(types.KeyboardButton(text="Назад"))
    model_id = await Model.get_id(model_name=model_name, brand_id=data['brand_id'])
    
    await message.answer("Выберите раздел", reply_markup=builder.as_markup(resize_keyboard=True,
                                                        input_field_placeholder='Выберите раздел'))
    
    await state.set_state(Advertisement.internal_section)
    
    data.update({'model_id': model_id, 'model_name': model_name, 'external_sections': external_sections})
    await state.set_data(data=data)


@router.message(Advertisement.internal_section, F.text.casefold() == "назад")
async def back_to_model(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.pop('model_id')
    data.pop('model_name')
    
    await state.set_data(data)
    await state.set_state(Advertisement.model)
    await model(message, state)


# @router.message(Advertisement.internal_section, F.text.in_(ExternalMenu.get_names()))
@router.message(Advertisement.internal_section)
async def lower_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    external_section_name = data.get('external_section_name', message.text)

    try:
        section_id = next(filter(
                    lambda external_section: external_section.section_name == external_section_name,
                                            data['external_sections'])).id
    except StopIteration:
        await message.answer("К сожалению, нет такого раздела, пожалуйста, выберите из предложенных")
        return

    internal_names = await InternalMenu.get_names(section_id)

    builder = ReplyKeyboardBuilder()
    buttons = []

    for i, name in enumerate(internal_names, start=1):
        buttons.append(types.KeyboardButton(text=name))
        if i % max_detail_menu_sections_in_row == 0:
            builder.row(*buttons)
            buttons.clear()

    if buttons:
        builder.row(*buttons)
        
    builder.row(types.KeyboardButton(text="Назад"))

    await message.answer("Отлично! Еще одно уточнение;)",
                         reply_markup=builder.as_markup(
                            resize_keyboard=True,
                            input_field_placeholder=f"Раздел {external_section_name}"))
    
    await state.set_state(Advertisement.selection_confirm)
    data.update({'external_section_id': section_id, 'external_section_name': external_section_name})
    await state.set_data(data=data)


@router.message(Advertisement.selection_confirm, F.text.casefold() == "назад")
async def back_to_upper_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await state.set_data(data)
    await state.set_state(Advertisement.internal_section)
    await external_section(message, state)


@router.message(Advertisement.selection_confirm)
async def lower_menu_end(message: types.Message, state: FSMContext):
    data = await state.get_data()

    internal_names = await InternalMenu.get_names(data['external_section_id'])
    internal_name = data.get('internal_section_name', message.text)
    
    if internal_name not in internal_names:
        await message.answer(f'Нет такого раздела. Пожалуйста, выберите из предложенных')
        return
    
    internal_section_id = await InternalMenu.get_id(section_name=internal_name,
                                                   external_section_id=data['external_section_id'])

    data.update({'internal_section_id': internal_section_id, 'internal_section_name': internal_name})

    keyboard = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="Назад")],],
                                         resize_keyboard=True)
    await state.set_state(Advertisement.detail_name)
    await state.set_data(data=data)
    await message.answer("Напишите название объявления, длина названия не должна превышать 32 символа",
                         reply_markup=keyboard)


@router.message(Advertisement.detail_name, F.text.casefold() == "назад")
async def back_to_lower_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.pop('internal_section_id')
    await state.set_data(data)
    await state.set_state(Advertisement.internal_section)
    await lower_menu(message, state)


@router.message(Advertisement.detail_name)
async def detail_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    detail_name = data.get('detail_name', message.text)
    data.update({'detail_name': detail_name})

    await state.set_data(data=data)
    await state.set_state(Advertisement.image)
    await message.answer("Прикрепите фото детали(сохранится всего одно).")


@router.message(Advertisement.image, F.text.casefold() == "назад")
async def back_to_lower_menu_end(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.pop('detail_name')
    await state.set_data(data)
    await state.set_state(Advertisement.detail_name)
    await lower_menu_end(message, state)


@router.message(Advertisement.image)
async def detail_image(message: types.Message, state: FSMContext):
    # TODO: can user skip this step? 
    data = await state.get_data()

    try:
        image_id = data.get('image_id') if not message.photo else message.photo[-1].file_id
        data.update({'image_id': image_id}) # а если не прислали фото?
    except KeyError:
        await message.answer("Вы можете пропустить этот шаг или отправить фото")
        return

    await state.set_data(data=data)
    await state.set_state(Advertisement.description)
    await message.answer("Добавим описание к объявлению(длина не должна превышать 256 символов)")


@router.message(Advertisement.description, F.text.casefold() == "назад")
async def back_to_detail_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.pop('image_id')
    await state.set_data(data)
    await state.set_state(Advertisement.detail_name)
    await detail_name(message, state)


@router.message(Advertisement.description)
async def detail_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    description = data.get('description', message.text)
    data.update({'description': description})
    
    await state.set_data(data=data)
    await state.set_state(Advertisement.price)
    await message.answer("Укажите цену товара")


@router.message(Advertisement.price, F.text.casefold() == "назад")
async def detail_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.pop('description')
    await state.set_data(data)
    await state.set_state(Advertisement.image)
    await detail_image(message, state)


@router.message(Advertisement.price)
async def detail_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    try:
        data.update({'price': int(message.text)})
    except ValueError:
        await message.answer("Пожалуйста, введите целое число")
        return
    
    await state.set_data(data=data)

    caption = Detail.make_caption(data['detail_name'], data['price'],
                                    message.from_user.username, data['description'])
    
    await message.answer_photo(data['image_id'], caption=caption)
    buttons = [
        [
            types.KeyboardButton(text='Сохранить'),
            types.KeyboardButton(text='Назад')
        ],
    ]
    placeholder = f"Осталось объявлений: {data['available_advertisements']}"
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, input_field_placeholder=placeholder,
                                         resize_keyboard=True)
    await state.set_state(Advertisement.final)
    await state.set_data(data)
    await message.answer("Ваше объявление будет выглядеть следующим образом. Если все верно, нажмите 'Сохранить', в ином случае вы можете изменить его с помощью кнопок 'Назад'",
                         reply_markup=keyboard)
    

@router.message(Advertisement.final, F.text.casefold() == 'назад')
async def save_advertisement(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.pop('price')
    await state.set_data(data)
    await state.set_state(Advertisement.description)
    await detail_description(message, state)


@router.message(Advertisement.final, F.text.casefold() == 'сохранить')
async def save_advertisement(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await Detail.create_advertisement(data['detail_name'], message.from_user.id, data['external_section_id'],
                        data['internal_section_id'], data['brand_id'], data['model_id'], data['description'],
                        data['image_id'], data['price'])

    await message.answer(f"Отлично, ваше объявление сохранено и доступно для просмотра. Доступно еще: {data['available_advertisements']} ",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.clear()