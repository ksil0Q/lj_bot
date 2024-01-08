from __future__ import annotations

from peewee import PrimaryKeyField, CharField, ForeignKeyField, BooleanField, IntegrityError
from typing import Dict, Any
import logging


from .basemodel import BaseModel
from .user_car import UserCar
from loader import psql_manager


class Customer(BaseModel):
    id = PrimaryKeyField()
    username = CharField(32)
    car_id = ForeignKeyField(UserCar, null=True)
    blocked = BooleanField(default=False)
    blocking_reason = CharField(1024)
    commands = ['/menu', '/change_my_car', '/my_office', '/help', '/become_a_seller', '/choose_a_tariff']

    class Meta:
        db_table = 'customers'


    @classmethod
    async def block_user(cls, id: int, reason: str) -> bool:
        updated_fields = await psql_manager.execute(
            cls.update(blocked=True, blocking_reason=reason)
            .where(cls.id == id))

        if updated_fields:
            return True
        
        return False
    

    @classmethod
    async def unblock_user(cls, id: int) -> bool:
        updated_fields = await psql_manager.execute(
            cls.update(blocked=False, blocking_reason=None)
            .where(cls.id == id))

        if updated_fields:
            return True
        
        return False
    

    @classmethod
    async def get_or_create(cls, id: int, username: str) -> Customer:
        customer = await psql_manager.get(cls, id=id, username=username)

        if not customer:
            customer = await psql_manager.create(cls, id=id, username=username)

        return customer
    

    @classmethod
    async def save_car(cls, user_id: int, brand_id: int, model_id: int) -> bool:
        customer = await psql_manager.get(cls.select(cls.car_id).where(cls.id==user_id))
        
        async with psql_manager.atomic() as transaction:
            try:
                if not customer.car_id:
                    user_car = await psql_manager.create(UserCar, brand_id=brand_id, model_id=model_id)
                    await psql_manager.execute(cls.update(car_id=user_car.id).where(cls.id==user_id))
                else:
                    user_car = await psql_manager.get(UserCar, id=customer.car_id)

                    await psql_manager.execute(
                            UserCar.update(brand_id=brand_id, model_id=model_id)
                            .where(UserCar.id==customer.car_id))

                return True
            except IntegrityError:
                transaction.rollback()
                return False


    @classmethod
    async def get_brand_model(cls, user_id: int) -> Dict[str, int]:
        query = await psql_manager.execute(
            UserCar.select(cls, UserCar)
                .join(cls)
                .where(cls.id==user_id))

        return {'brand_id': query[0].brand_id, 'model_id': query[0].model_id}
