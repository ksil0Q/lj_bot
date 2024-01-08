from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
import logging


from models import Customer


class BlockerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        
        customer = await Customer.get_or_none(Customer.id==event.from_user.id)

        # TODO: add a reason of blocking field in model
        if customer and customer.blocked:
            await event.answer('По каким-то причинам вы оказались в черном списке')
            return
        
        result = await handler(event, data)
        return result