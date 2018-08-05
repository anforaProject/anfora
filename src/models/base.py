from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase

#db = SqliteDatabase('zinat.db')
db = PostgresqlExtDatabase(
    'anforadb',  # Required by Peewee.
    user='postgres',  # Will be passed directly to psycopg2.
    host='localhost',  # Ditto.
    port='5432',
)

class BaseModel(Model):
    class Meta:
        database = db

    def __exclude(self, lst=[]):
        from models.user import UserProfile
        return [UserProfilepassword] + lst
