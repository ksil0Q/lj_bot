from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.dispatcher.flags import get_flag
import logging


from models import Seller


class SellerOnlyMiddleware(BaseMiddleware):
    flag = 'seller_only'
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        seller_only = get_flag(data, self.flag, default=False)

        if seller_only:
            seller = await Seller.get_or_none(Seller.id==event.from_user.id)
            if not seller:
                await event.answer("К сожалению, вы не можете выкладывать объявления. Чтобы стать продавцом: /become_a_seller")
                return
            if not seller.available_advertisements:
                await event.answer("На данный момент Вы достигли лимита по объявлениям. Выберите тариф: /choose_a_tariff")
                return

            result = await handler(event, data)
            return result
        
        result = await handler(event, data)
        return result