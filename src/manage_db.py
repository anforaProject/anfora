from models.base import db

from models.user import User
from models.album import Album
from models.photo import Photo
from models.albumRelation import RelationAlbumPhoto
from models.token import Token


def connect():
    db.connect()
    
def create_tables():
    tables = [User, Album, Photo, Token, RelationAlbumPhoto]

    for table in tables:
        if not table.table_exists():
            table.create_table()
