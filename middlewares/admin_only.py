from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.dispatcher.flags import get_flag
import logging

from models import Admin


class AdminOnlyMiddleware(BaseMiddleware):
    flag = 'admin_only'
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        admin_only = get_flag(data, self.flag, default=False)
        
        if admin_only:
            admin = await Admin.get_or_none(Admin.id==event.from_user.id)
            
            if not admin:
                await event.answer('Эта функция Вам не доступна')
                return
            result = await handler(event, data)
            return result
        
        result = await handler(event, data)
        return result