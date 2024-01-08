from __future__ import annotations
from typing import Any
from peewee import PrimaryKeyField, IntegerField
from datetime import datetime
from hashlib import sha256
import logging


from .basemodel import BaseModel
from loader import max_code_len, psql_manager


class VerificationCode(BaseModel):
    id = PrimaryKeyField()
    code = IntegerField()


    class Meta:
        db_table = 'verification_codes'


    @classmethod
    async def new(cls, bill_id: int, user_id: int, tariff_id: int,
               creation_date: datetime, expiration_date: datetime, bill = None) -> VerificationCode:
        
        code = cls.generate_code(bill_id, user_id, tariff_id,
                                creation_date, expiration_date)
        
        if not bill:        
            code_entity = await psql_manager.create(cls, code=code)
        else:
            code_entity = await psql_manager.get(cls, id=bill.code_id)
            code_entity.code = code

            await psql_manager.update(code_entity)

        return code_entity
    

    @staticmethod
    def generate_code(bill_id: int, user_id: int, tariff_id: int,
               creation_date: datetime, expiration_date: datetime) -> int:
        
        msg = f"{bill_id}{user_id}{tariff_id}{creation_date}{expiration_date}".encode()
        hash = sha256(msg, usedforsecurity=True)
        hexdigest = hash.hexdigest()
        return int(hexdigest, 16) % 10 ** max_code_len
