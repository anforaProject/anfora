from peewee import Model
from settings import (DB_USER, DB_NAME, DB_PORT, DB_HOST)
#from playhouse.postgres_ext import PostgresqlExtDatabase
from peewee_async import Manager

from peewee_async import PostgresqlDatabase

#db = SqliteDatabase('zinat.db')
db = PostgresqlDatabase(
    DB_NAME,  # Required by Peewee.
    user=DB_USER,  # Will be passed directly to psycopg2.
    host=DB_HOST,  # Ditto.
    port=DB_PORT,
)
import peeweedbevolve

class BaseModel(Model):
    class Meta:
        database = db
