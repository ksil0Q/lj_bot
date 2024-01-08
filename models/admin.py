from __future__ import annotations

from peewee import PrimaryKeyField, CharField, DoesNotExist
from typing import List, Optional, Any
import logging


from .basemodel import BaseModel
from loader import psql_manager


class Admin(BaseModel):
    id = PrimaryKeyField()
    username = CharField(32)
    commands = ['/menu', '/change_my_car', '/my_office', '/help', '/confirm_payment',
                '/block_a_user', '/unblock_a_user', '/create_advertisement',
                '/close_advertisement']


    class Meta:
        db_table = 'admins'

    
    @classmethod
    async def get_usernames(cls) -> List[str]:
        usernames_query = await psql_manager.execute(cls.select())
        return [row.username for row in usernames_query]
