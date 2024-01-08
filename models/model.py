from peewee import PrimaryKeyField, CharField, ForeignKeyField
from typing import List
import logging


from .brand import Brand
from .basemodel import BaseModel
from loader import psql_manager


class Model(BaseModel):
    id = PrimaryKeyField()
    brand_id = ForeignKeyField(Brand, null=True)
    model_name = CharField(48)
    cyrillic_name = CharField(48)

    class Meta:
        db_table = 'models'


    @classmethod
    async def get_id(cls, model_name: str, brand_id: int) -> int:
        id_entity = await psql_manager.get(
            cls.select(cls.id)\
            .where(cls.model_name==model_name, cls.brand_id==brand_id))
        
        return id_entity.id
        
    @classmethod
    async def get_names(cls, brand_id: int) -> List[str]:
        names = await psql_manager.execute(
            cls.select()\
            .join(Brand)\
            .where(Brand.id == brand_id))
        
        return [name.model_name for name in names]