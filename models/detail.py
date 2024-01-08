from typing import List, Dict, Any
from peewee import PrimaryKeyField, CharField, ForeignKeyField, DoubleField, BooleanField, IntegrityError, JOIN
import logging


from .basemodel import BaseModel
from .external_menu import ExternalMenu
from .internal_menu import InternalMenu
from .brand import Brand
from .model import Model
from .seller import Seller
from loader import psql_manager


class Detail(BaseModel):
    id = PrimaryKeyField()
    detail_name = CharField(32)
    seller_id = ForeignKeyField(Seller)
    external_section_id = ForeignKeyField(ExternalMenu)
    internal_section_id = ForeignKeyField(InternalMenu)
    brand_id = ForeignKeyField(Brand)
    model_id = ForeignKeyField(Model)
    description = CharField(256)
    image_id = CharField(128)
    price = DoubleField()
    closed = BooleanField(default=False)


    class Meta:
        db_table = 'details'


    @classmethod
    async def get_details(cls, external_section_id: int, internal_section_id: int,
                    brand_id: int, model_id: int) -> List[Dict[str, Any]]:

        query = cls.select(cls.id, cls.detail_name, cls.image_id, cls.description, cls.price, cls.seller_id, Seller.username)\
            .join(Seller, JOIN.INNER, on=(Seller.id == cls.seller_id))\
            .where(cls.external_section_id==external_section_id,
                    cls.internal_section_id==internal_section_id,
                    cls.brand_id==brand_id,
                    cls.model_id==model_id)
        
        details = await psql_manager.execute(query)

        result = []
        for detail in details:
            caption = cls.make_caption(detail.detail_name, detail.price,
                                       detail.seller_id.username, detail.description, detail.id)
            
            result.append({'detail_name': detail.detail_name, 'image_id': detail.image_id, 'caption': caption})

        return result
    

    @staticmethod
    def make_caption(detail_name: str, price: int, username: str, description: str, id: int = 0) -> str:
        return f"Номер в системе: {id}\nНазвание: {detail_name}\nЦена: {price} руб.\nПродавец: @{username}\nОписание: {description}"
    

    @classmethod
    async def create_advertisement(cls, detail_name: str, seller_id: int, external_section_id: int,
                        internal_section_id, brand_id: int, model_id: int, description: str,
                        image_id: str, price: int):
        
        async with psql_manager.atomic() as transaction:
            try:
                seller = await Seller.get_or_none(id=seller_id)
                if not seller:
                    raise IntegrityError(f"No user with id: {seller_id}")
                
                await psql_manager.execute(
                    Seller.update(available_advertisements = seller.available_advertisements - 1))

                await psql_manager.create(Detail, detail_name=detail_name, seller_id=seller_id,
                              external_section_id=external_section_id,
                              internal_section_id=internal_section_id,
                              brand_id=brand_id, model_id=model_id,
                              description=description, image_id=image_id, price=price)
                
            except IntegrityError:
                transaction.rollback()


    @classmethod
    async def get_all_by_user_id(cls, id: int) -> List[Dict[str, Any]]:
        query = cls.select(cls.id, cls.detail_name, cls.image_id, cls.description, cls.price, cls.seller_id, Seller.username)\
                .join(Seller, JOIN.INNER, on=(Seller.id == cls.seller_id)\
                .where(cls.seller_id==id))

        details = await psql_manager.execute(query)

        result = []
        for detail in details:
            caption = cls.make_caption(detail.detail_name, detail.price,
                                       detail.seller_id.username, detail.description, detail.id)
            
            result.append({'detail_name': detail.detail_name, 'image_id': detail.image_id, 'caption': caption})

        return result


    @classmethod
    async def close_advertisement(cls, id: int) -> bool:
        query = cls.delete().where(cls.id==id)

        closed = await psql_manager.execute(query)
    
        return closed and True or False