from typing import List, Any
from peewee import PrimaryKeyField, CharField


from loader import psql_manager
from .basemodel import BaseModel


class ExternalMenu(BaseModel):
    id = PrimaryKeyField()
    section_name = CharField(32)

    class Meta:
        db_table = 'external_menu_sections'
        
    
    @classmethod
    async def get_sections(cls) -> List[Any]:
        sections_query = await psql_manager.execute(cls.select())
        return [section for section in sections_query]
    

    @classmethod
    async def get_names(cls) -> List[str]:
        names_query = await psql_manager.execute(cls.select())
        names = [row.section_name for row in names_query]
        return names