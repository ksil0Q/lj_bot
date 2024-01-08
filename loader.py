import os
from peewee_async import PostgresqlDatabase, Manager
from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
import asyncio

load_dotenv()


# database
db = PostgresqlDatabase(database=os.environ.get('DATABASE'),
                        user=os.environ.get('USER'),
                        password=os.environ.get('PASSWORD'),
                        host=os.environ.get('HOST'),
                        port=os.environ.get('PORT'))
psql_manager = Manager(database=db, loop=None)

# bot
bot = Bot(token=os.environ.get('API_TOKEN'), parse_mode='HTML')
dp = Dispatcher()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # fix for peewee_async on win

max_brands_in_row = int(os.environ.get('MAX_BRANDS_IN_ROW'))
max_models_in_row = int(os.environ.get('MAX_MODELS_IN_ROW'))

max_detail_menu_sections_in_row = int(os.environ.get('MAX_DETAIL_MENU_SECTIONS_IN_ROW'))
max_tariffs_in_row = int(os.environ.get('MAX_TARIFFS_IN_ROW'))
max_inline_buttons = int(os.environ.get('MAX_INLINE_BUTTONS'))
max_code_len = int(os.environ.get('MAX_CODE_LEN'))