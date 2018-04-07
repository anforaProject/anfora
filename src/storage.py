import datetime
import uuid
import binascii
import os

from peewee import *
from playhouse.shortcuts import model_to_dict

db = SqliteDatabase('zinat.db')



def createId():
    return str(uuid.uuid4())
    

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    admin = BooleanField(default=False)

default_exclude = [User.password]
    
class Album(BaseModel):
    name = CharField()
    creted_date = DateTimeField(default=datetime.datetime.now)
    public = BooleanField(default=False)
    user = ForeignKeyField(User, backref='albums')

    def json(self):
        return model_to_dict(self, exclude=default_exclude)

class Photo(BaseModel):
    title = CharField()
    identifier = CharField(default=createId, unique=True)
    upload_date = DateTimeField(default=datetime.datetime.now)
    public = BooleanField(default=True)
    user = ForeignKeyField(User, backref='photos')

    def __str__(self):
        return "{} - {} - {}".format(self.title, self.identifier, self.upload_date)

    def identify(self):
        return str(self.identifier)

    def albums(self):
        query = (RelationAlbumPhoto
                .select()
                .where(RelationAlbumPhoto.photo==self)
        )

        return [model_to_dict(rel,exclude=[User.password, RelationAlbumPhoto.photo, RelationAlbumPhoto.id]) for rel in query]

    def json(self):
        return model_to_dict(self, exclude=default_exclude, extra_attrs=["albums"])

class RelationAlbumPhoto(BaseModel):

    album = ForeignKeyField(Album)
    photo = ForeignKeyField(Photo)

    class Meta:
        indexes = (
        (('album', 'photo'), True),
        )

class Token(BaseModel):

    key = CharField(primary_key=True)
    user = ForeignKeyField(User, on_delete='CASCADE')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()
        
def connect():
    db.connect()
    
def create_tables():
    tables = [User, Album, Photo, Token, RelationAlbumPhoto]

    for table in tables:
        if not table.table_exists():
            table.create_table()
