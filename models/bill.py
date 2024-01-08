from __future__ import annotations

from loader import db, psql_manager
from typing import List, Any, Dict
from datetime import datetime
from peewee import PrimaryKeyField, ForeignKeyField, BooleanField, DateTimeField,\
                    IntegrityError, JOIN
import logging


from .seller import Seller
from .tariff import Tariff
from loader import psql_manager
from .basemodel import BaseModel
from .verification_code import VerificationCode


class Bill(BaseModel):
    id = PrimaryKeyField()
    user_id = ForeignKeyField(Seller)
    tariff_id = ForeignKeyField(Tariff)
    paid = BooleanField(default=False)
    creation_date = DateTimeField()
    expiration_date = DateTimeField()
    code_id = ForeignKeyField(VerificationCode)


    class Meta:
        db_table = 'bills'


    @classmethod
    async def create_or_update(cls, user_id: int, tariff_id: int, closed: bool,
                         creation_date: datetime, expiration_date: datetime) -> Bill:
        
        bill = await cls.get_or_none(user_id=user_id, tariff_id=tariff_id,
                                               paid=False)

        verification_code = await VerificationCode.new(user_id, tariff_id,
                                                       closed, creation_date,
                                                       expiration_date, bill)
        
        if bill:
            await psql_manager.execute(
                cls.update(expiration_date = expiration_date, code_id = verification_code.id)\
                .where(cls.id == bill.id))
            
        else:
            bill = await psql_manager.create(cls, user_id=user_id, tariff_id=tariff_id,
                                              closed=closed, creation_date=creation_date,
                                              expiration_date=expiration_date,
                                              code_id=verification_code.id)

        return bill


    @classmethod
    async def get_unpaid_by_id(cls) -> List[Dict[str, Any]]:      
        unpaid_bills = await psql_manager.execute(cls.select(cls.id, cls.tariff_id, cls.code_id, cls.user_id,
                                  VerificationCode.code,
                                  Seller.username,
                                  Tariff.tariff_name
                                  )\
            .join(Seller, on=(Seller.id==cls.user_id))\
            .join(Tariff, on=(Tariff.id==cls.tariff_id))\
            .join(VerificationCode, on=(VerificationCode.id==cls.code_id))\
            .where(cls.paid==False)) 
        
        if not unpaid_bills:
            return []

        unpaid_user_fields = []
        for unpaid in unpaid_bills:
            unpaid_user_fields.append({'bill_id': unpaid.id, 'username': unpaid.user_id.username,
                                       'tariff_name': unpaid.tariff_id.tariff_name,
                                       'code': unpaid.code_id.code})

        return unpaid_user_fields
    

    @staticmethod
    def get_unpaid_message_text(unpaid_rows: List[Any]) -> str:
        messages = []

        for i, row in enumerate(unpaid_rows, start=1):
            temp = f'{i}. Имя пользователя: @{row["username"]}\nТариф: {row["tariff_name"]}\nКодик: {row["code"]}\n'
            messages.append(temp)
        
        return '\n'.join(messages)
    

    @classmethod
    async def confirm_payment(cls, bill_id: int) -> bool:
        async with psql_manager.atomic() as transaction:
            try:
                unconfirmed_bill = await psql_manager.execute(cls.select(cls.user_id, cls.tariff_id, cls.paid,
                                                            Seller.id,
                                                            Seller.available_advertisements,
                                                            Tariff.advertisements_count)\
                    .join(Seller, on=(cls.user_id==Seller.id))\
                    .join(Tariff, on=(cls.tariff_id==Tariff.id))\
                    .where(cls.id==bill_id))
                
                unconfirmed_bill = unconfirmed_bill[0]

                Seller.update(available_advertisements=\
                              (unconfirmed_bill.user_id.available_advertisements +\
                               unconfirmed_bill.tariff_id.advertisements_count))\
                    .where(Seller.id==unconfirmed_bill.user_id.id)\
                    .execute()
                
                updated = await psql_manager.execute(cls.update(paid = True)\
                                           .where(cls.id == bill_id))

                if not updated:
                    raise IntegrityError()

                return True
            except IntegrityError:
                transaction.rollback()
                return False


    @classmethod
    async def get_code(cls, bill_id) -> int:    
        code = await psql_manager.execute(VerificationCode.select(VerificationCode)\
                .join(cls, JOIN.INNER, on=(VerificationCode.id==cls.code_id))\
                .where(cls.id==bill_id))
        
        return code[0].code
