from peewee import Model, DoesNotExist
from typing import Any, Optional
import logging


from loader import db, psql_manager


class BaseModel(Model):
     
    class Meta:
        database = db

    
    @classmethod
    async def get_or_none(cls, *query: Any, **filters: Any) -> Optional[Model]:
        try:
            return await psql_manager.get(cls, *query, **filters)
        except DoesNotExist:
            logging.info(f"{cls.__name__}DoesNotExist:\nQuery {query}\nFilters {filters}")