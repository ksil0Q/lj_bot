from __future__ import annotations

from peewee import PrimaryKeyField, CharField, IntegerField
from typing import Any
import logging


from .basemodel import BaseModel
from loader import psql_manager


class Seller(BaseModel):
    id = PrimaryKeyField()
    username = CharField(32)
    available_advertisements = IntegerField()
    commands = ['/menu', '/change_my_car', '/my_office', '/help',
                '/create_advertisement', '/close_advertisement', '/choose_a_tariff']

    class Meta:
        db_table = 'sellers'


    @classmethod
    async def get_or_create(cls, id: int, username: str) -> Seller:
        seller = await psql_manager.get(cls, id=id, username=username)

        if not seller:
            seller = await psql_manager.create(cls, id=id, username=username)

        return seller
