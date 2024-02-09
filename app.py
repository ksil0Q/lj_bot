import asyncio
import logging
import ssl
from aiogram import Bot
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


import loader
from loader import bot, dp
from middlewares import BlockerMiddleware
from handlers import common, seller_role, customer_role, car_choosing, detail_menu,\
    creating_advertisement, confirm_payment, user_blocking, closing_advertisement


async def on_startup(bot: Bot) -> None:
    logging.info("Bot has been started")
    await bot.set_webhook(f"{loader.WEBHOOK_URL}:{loader.WEB_SERVER_PORT}{loader.WEBHOOK_PATH}")
    logging.info("Webhook has been set up")


async def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('aiogram').setLevel(logging.DEBUG)

    dp.include_routers(customer_role.router, seller_role.router, car_choosing.router,
                       detail_menu.router, creating_advertisement.router, confirm_payment.router,
                       user_blocking.router, closing_advertisement.router,
                       common.router) # that router must always be the last one
    dp.message.outer_middleware(BlockerMiddleware())

    dp.startup.register(on_startup)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )

    webhook_requests_handler.register(app, path=loader.WEBHOOK_PATH)

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(loader.WEBHOOK_SSL_CERT, loader.WEBHOOK_SSL_PRIV)

    setup_application(app, dp, bot=bot)

    await web._run_app(app, host=loader.WEB_SERVER_HOST, port=loader.WEB_SERVER_PORT, ssl_context=context)


if __name__ == '__main__':
    asyncio.run(main())
