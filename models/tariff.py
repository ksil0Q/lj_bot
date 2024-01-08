from typing import List, Dict, Any
from peewee import PrimaryKeyField, CharField, IntegerField
import logging


from .basemodel import BaseModel
from loader import psql_manager


class Tariff(BaseModel):
    id = PrimaryKeyField()
    tariff_name = CharField(32)
    description = CharField(128)
    tariff_price = IntegerField()
    advertisements_count = IntegerField(null=False)


    class Meta:
        db_table = 'tariffs'


    @classmethod
    async def get_values(cls) -> List[Dict[str, Any]]:
        values = await psql_manager.execute(cls.select(cls))
        
        return [{'id': row.id, 'tariff_name': row.tariff_name,
                 'description': row.description, 'tariff_price': row.tariff_price}
                 for row in values]
    
    
    @classmethod
    async def get_names(cls) -> List[str]:
        names = await psql_manager.execute(cls.select(cls.tariff_name))
        return [row.tariff_name for row in names]
    

    @classmethod
    def format_for_message(cls, tariffs: List[Dict[str, Any]]) -> str:
        result = ''
        for tariff in tariffs:
            temp = "{0:s}:\n{1:s}\n{2:d}руб.".format(tariff['tariff_name'],
                                                     tariff['description'],
                                                     tariff['tariff_price'])
            
            result = "{0:s}\n\n{1:s}".format(result, temp)

        return result
    
    
    @classmethod
    async def get_id_by_name(cls, name: str) -> int:
        id_entity = await psql_manager.get(cls, tariff_name=name)
        return id_entity.id
