from peewee import ForeignKeyField

from .base import BaseModel
from .album import Album
from .status import Status

class RelationAlbumStatus(BaseModel):

    album = ForeignKeyField(Album)
    photo = ForeignKeyField(Status)

    class Meta:
        indexes = (
        (('album', 'photo'), True),
        )
