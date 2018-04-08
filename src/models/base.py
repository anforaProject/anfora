from peewee import *

db = SqliteDatabase('zinat.db')

class BaseModel(Model):
    class Meta:
        database = db

    def __exclude(self, lst=[]):
        from models.user import User
        return [User.password] + lst
