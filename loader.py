import os
from peewee_async import PostgresqlDatabase, Manager
from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
import asyncio

load_dotenv()


# database
db = PostgresqlDatabase(database=os.environ.get('DATABASE_NAME'),
                        user=os.environ.get('USER'),
                        password=os.environ.get('PASSWORD'),
                        host=os.environ.get('DB_HOST'),
                        port=os.environ.get('DB_PORT'))
psql_manager = Manager(database=db, loop=None)

# bot
bot = Bot(token=os.environ.get('API_TOKEN'), parse_mode='HTML')
dp = Dispatcher()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # fix for peewee_async on win

WEB_SERVER_HOST=os.environ.get('WEB_SERVER_HOST')
WEB_SERVER_PORT=int(os.environ.get('WEB_SERVER_PORT'))

WEBHOOK_PATH=os.environ.get('WEBHOOK_PATH')
WEBHOOK_URL=os.environ.get('WEBHOOK_URL')

WEBHOOK_SSL_PRIV=os.environ.get("WEBHOOK_SSL_PRIV")
WEBHOOK_SSL_CERT=os.environ.get("WEBHOOK_SSL_CERT")


max_brands_in_row = int(os.environ.get('MAX_BRANDS_IN_ROW'))
max_models_in_row = int(os.environ.get('MAX_MODELS_IN_ROW'))

max_detail_menu_sections_in_row = int(os.environ.get('MAX_DETAIL_MENU_SECTIONS_IN_ROW'))
max_tariffs_in_row = int(os.environ.get('MAX_TARIFFS_IN_ROW'))
max_inline_buttons = int(os.environ.get('MAX_INLINE_BUTTONS'))
max_code_len = int(os.environ.get('MAX_CODE_LEN'))
