import asyncio
import logging


from loader import bot, dp
from middlewares import BlockerMiddleware
from handlers import common, seller_role, customer_role, car_choosing, detail_menu,\
    creating_advertisement, confirm_payment, user_blocking, closing_advertisement


async def startup():
    logging.basicConfig(level=logging.INFO)

    dp.include_routers(customer_role.router, seller_role.router, car_choosing.router,
                       detail_menu.router, creating_advertisement.router, confirm_payment.router,
                       user_blocking.router, closing_advertisement.router,
                       common.router) # that router always must be the last one
    dp.message.outer_middleware(BlockerMiddleware())
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(startup())
