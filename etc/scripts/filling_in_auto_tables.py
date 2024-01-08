import os
import requests
from typing import Dict, List, Any


from peewee import PostgresqlDatabase, PrimaryKeyField, CharField, BooleanField, IntegerField, Model as M
from dotenv import load_dotenv


load_dotenv()
db = PostgresqlDatabase(database=os.environ.get('DATABASE'),
                        user=os.environ.get('USER'),
                        password=os.environ.get('PASSWORD'),
                        host=os.environ.get('HOST'),
                        port=os.environ.get('PORT'))
    

class BaseModel(M):
    class Meta:
        database = db


class Brand(BaseModel):
    id = PrimaryKeyField()
    brand_name = CharField(16)
    cyrillic_name = CharField(16)
    popular = BooleanField()
    country = CharField(16)

    class Meta:
        db_table = 'brands'


class Model(BaseModel):
    id = PrimaryKeyField()
    brand_id = IntegerField()
    model_name = CharField(48)
    cyrillic_name = CharField(48)

    class Meta:
        db_table = 'models'


def get_cars_json(url: str) -> List[Dict[str, Any]]:
    return requests.get(url).json()


def insert_brands_and_models(json: List):
    for i, brand in enumerate(json):
        Brand.insert(id=i+1, brand_name=brand['name'], cyrillic_name=brand['cyrillic-name'], popular=brand['popular'], country=brand['country']).execute()
        for model in brand['models']:
            Model.insert(brand_id=i+1, model_name=model['name'], cyrillic_name=model['cyrillic-name']).execute()



json = get_cars_json('https://cars-base.ru/api/cars?full=1')
insert_brands_and_models(json)