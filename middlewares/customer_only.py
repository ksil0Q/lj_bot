from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.dispatcher.flags import get_flag
import logging


from models import Customer


class CustomerOnlyMiddleware(BaseMiddleware):
    flag = 'customer_only'
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        customer_only = get_flag(data, self.flag, default=False)
        
        if customer_only:
            customer = await Customer.get_or_none(Customer.id==event.from_user.id)

            if not customer:
                await event.answer("Для использования площадки в качестве покупателя: /become_a_customer\
                                   В качестве продавца /become_a_seller")
                return

            result = await handler(event, data)
            return result
        
        result = await handler(event, data)
        return result