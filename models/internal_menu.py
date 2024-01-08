from typing import List, Dict, Any
from peewee import PrimaryKeyField, CharField, ForeignKeyField
import logging


from loader import psql_manager
from .basemodel import BaseModel
from .external_menu import ExternalMenu


class InternalMenu(BaseModel):
    id = PrimaryKeyField()
    section_name = CharField(32)
    external_section_id = ForeignKeyField(ExternalMenu)

    class Meta:
        db_table = 'internal_menu_sections'


    @classmethod
    async def get_id(cls, section_name: str, external_section_id: int) -> int:
        id_entity = await psql_manager.get(
            cls.select(cls.id)\
            .where(cls.section_name==section_name,
                   cls.external_section_id==external_section_id))
        
        return id_entity.id
    

    @classmethod
    async def get_names(cls, external_section_id: int) -> List[str]:
        names = await psql_manager.execute(
            cls.select(cls.section_name)\
                .join(ExternalMenu)\
                .where(ExternalMenu.id==external_section_id))
        
        return [row.section_name for row in names]
    

    @classmethod
    async def get_names_and_ids(cls, external_section_id: int) -> List[Dict[str, Any]]:
        id_and_names = await psql_manager.execute(
            cls.select(cls.id, cls.section_name)\
                .join(ExternalMenu)\
                .where(ExternalMenu.id==external_section_id))
        
        return [{'id': row.id, 'section_name': row.section_name} for row in id_and_names]