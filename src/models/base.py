from peewee import *
from settings import (DB_USER, DB_NAME, DB_PORT, DB_HOST)
from playhouse.postgres_ext import PostgresqlExtDatabase

#db = SqliteDatabase('zinat.db')
db = PostgresqlExtDatabase(
    DB_NAME,  # Required by Peewee.
    user=DB_USER,  # Will be passed directly to psycopg2.
    host='localhost',  # Ditto.
    port=DB_PORT,
)

class BaseModel(Model):
    class Meta:
        database = db

    def __exclude(self, lst=[]):
        from models.user import UserProfile
        return [UserProfilepassword] + lst
