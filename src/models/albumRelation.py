from peewee import ForeignKeyField

from .base import BaseModel
from .album import Album
from .photo import Photo

class RelationAlbumPhoto(BaseModel):

    album = ForeignKeyField(Album)
    photo = ForeignKeyField(Photo)

    class Meta:
        indexes = (
        (('album', 'photo'), True),
        )
