from models.base import db

from models.user import User
from models.album import Album
from models.photo import Photo
from models.albumRelation import RelationAlbumPhoto
from models.token import Token
from models.followers import FollowerRelation
from models.activity import Activity
from models.hashtags import Hashtag
from models.comment import Comment
from models.hashtag_used import HashtagUsed
from models.like import Like
from models.follow_request import FollowRequest

def connect():
    db.connect()

def create_tables():

    tables = [User, 
                Album, 
                Photo, 
                Token, 
                RelationAlbumPhoto, 
                FollowerRelation,
                Activity, 
                Hashtag, 
                HashtagUsed,
                Like,
                FollowRequest,
            ]


    for table in tables:
        if not table.table_exists():
            table.create_table()
