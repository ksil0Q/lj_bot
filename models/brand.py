from peewee import PrimaryKeyField, CharField, BooleanField
from typing import List, Any, Dict, Union
import logging

from .basemodel import BaseModel
from loader import psql_manager


class Brand(BaseModel):
    id = PrimaryKeyField()
    brand_name = CharField(32)
    cyrillic_name = CharField(32)
    popular = BooleanField()
    country = CharField(32)

    class Meta:
        db_table = 'brands'


    @classmethod 
    async def get_fields_of_popular_brands(cls, *args) -> Union[List[Dict[str, Any]], List[Any]]:
        """Method returns field of all brand rows, that have popular flag.
            Just because I want to do so."""

        brands = await psql_manager.execute(cls.select().where(cls.popular==True))

        fields = []
        try:
            for brand in brands:
                if len(args) == 1:
                    fields.append(getattr(brand, *args))
                    continue

                res = {}
                for attr in args:
                    res.update({attr: getattr(brand, attr)})
                fields.append(res)

        except AttributeError as a:
            raise AttributeError()
        
        return fields
    