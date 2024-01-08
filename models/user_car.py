from peewee import PrimaryKeyField, ForeignKeyField


from .basemodel import BaseModel
from .brand import Brand
from .model import Model


class UserCar(BaseModel):
    id = PrimaryKeyField()
    brand_id = ForeignKeyField(Brand, null=True)
    model_id = ForeignKeyField(Model, null=True)


    class Meta:
        db_table = 'user_cars'