from models.base import db

from models.user import User
from models.album import Album
from models.status import Status
from models.media import Media
from models.albumRelation import RelationAlbumStatus
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
                Status, 
                Token, 
                RelationAlbumStatus, 
                FollowerRelation,
                Activity,
                Comment, 
                Hashtag, 
                HashtagUsed,
                Like,
                FollowRequest,
                Media
            ]


    for table in tables:
        if not table.table_exists():
            table.create_table()
