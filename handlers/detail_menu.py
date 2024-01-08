from aiogram.filters import Command
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


from fsm_models.menu import DetailMenu
from button_switcher import ButtonSwitcher
from middlewares import CustomerOnlyMiddleware
from loader import max_detail_menu_sections_in_row
from models import ExternalMenu, InternalMenu, Customer, Detail


router = Router()
router.message.middleware(CustomerOnlyMiddleware())


@router.message(Command("menu"), flags={'customer_only': True})
@router.message(DetailMenu.upper_level, flags={'customer_only': True})
async def start_menu(message: types.Message, state: FSMContext):
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

    await message.answer("Выберите раздел", reply_markup=builder.as_markup(resize_keyboard=True,
                                                        input_field_placeholder='Выберите раздел'))
    await state.set_state(DetailMenu.lower_level)
    await state.set_data(external_sections)


# @router.message(DetailMenu.lower_level, F.text.in_(ExternalMenu.get_names()))
@router.message(DetailMenu.lower_level)
async def lower_menu(message: types.Message, state: FSMContext):
    external_sections = await state.get_data()

    try:
        section_id = next(filter(lambda external_section: external_section.section_name == message.text, external_sections)).id
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
                            input_field_placeholder=f"Раздел {message.text}"))
    
    await state.set_state(DetailMenu.selection_confirm)
    await state.set_data({'id': section_id, 'external_section': message.text})


@router.message(DetailMenu.selection_confirm, F.text.casefold() == "назад")
async def back_button(message: types.Message, state: FSMContext):
    await state.set_data({})
    await state.set_state(DetailMenu.upper_level)
    await start_menu(message, state)

    
@router.message(DetailMenu.selection_confirm)
async def final_of_menu(message: types.Message, state: FSMContext):
    external_section = await state.get_data()
    internal_fields = await InternalMenu.get_names_and_ids(external_section['id'])
    
    try:
        internal_section_id = next(filter(lambda internal_section:
                                          internal_section['section_name'] == message.text, internal_fields))['id']
    except StopIteration:
        await message.answer(f'Нет такого раздела {message.text}, веберите из предложенных')
        return
    
    await message.answer('Это может занять некоторое время...',
                         reply_markup=types.ReplyKeyboardRemove())
    

    brand_model = await Customer.get_brand_model(message.from_user.id)
    details = await Detail.get_details(external_section['id'],
                                       internal_section_id,
                                       brand_model['brand_id'],
                                       brand_model['model_id'])
    details_count = len(details)
    if not details_count:
        await message.answer("На выбранное авто не нашлось деталей")
        return
    
    builder = InlineKeyboardBuilder()
    switcher = ButtonSwitcher(details_count)
    
    for button in switcher.get_buttons():
        callback_data = f"num_{button}"
        builder.button(text=button, callback_data=callback_data)

    detail = details[0]
    await message.answer_photo(detail['image_id'], caption=detail['caption'],
                                        reply_markup=builder.as_markup())

    await state.clear()
    await state.set_data([details, switcher])
    await state.set_state(DetailMenu.inline_mode)


@router.callback_query(DetailMenu.inline_mode, F.data.startswith("num_"))
async def inline_mode(callback: types.CallbackQuery, state: FSMContext):
    details, switcher = await state.get_data()

    builder = InlineKeyboardBuilder()
    pressed_button = callback.data.removeprefix("num_")

    for button in switcher.get_buttons(pressed_button):
        callback_data = f"num_{button}"
        builder.button(text=button, callback_data=callback_data)

    detail = details[int(pressed_button) - 1]
    photo = types.InputMediaPhoto(media=detail['image_id'], caption=detail['caption'])

    await callback.message.edit_media(photo, reply_markup=builder.as_markup())
