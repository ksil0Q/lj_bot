from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from models import Detail
from handlers.common import my_office
from fsm_models import ClosingAdvertisement
from middlewares import SellerOnlyMiddleware


router = Router()
router.message.middleware(SellerOnlyMiddleware())


@router.message(Command('close_advertisement'), flags={'seller_only': True})
@router.message(ClosingAdvertisement.all_advertisemennts, flags={'seller_only': True})
async def get_all_advertisemennts(message: types.Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Отмена"))

    await message.answer("Введите номер объявления в системе для удаления",
                         reply_markup=builder.as_markup(resize_keyboard=True))
    
    await state.set_state(ClosingAdvertisement.closing)


@router.message(ClosingAdvertisement.closing, F.text.casefold() == "отмена")
async def cancel_button(message: types.Message, state: FSMContext):
    await state.set_data({}) # clear state data
    await state.clear()
    await my_office(message)


@router.message(ClosingAdvertisement.closing)
async def closing(message: types.Message, state: FSMContext):
    try:
        advertisement_id = int(message.text)
    except ValueError:
        builder = ReplyKeyboardBuilder()
        builder.row(types.KeyboardButton(text="Отмена"))
        await message.answer("Введите номер объявления в системе для удаления",
                             reply_markup=builder.as_markup(resize_keyboard=True))
        return
    
    closed = await Detail.close_advertisement(advertisement_id)
    
    if closed:
        await message.answer('Объявление успешно удалено',
                             reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Объявления с таким номером не существует',
                             reply_markup=types.ReplyKeyboardRemove())
        
    await state.clear()
