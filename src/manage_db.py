import psycopg2

from settings import (DB_USER, DB_NAME, DB_PORT, DB_HOST)

from models.base import db

from models.user import UserProfile
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

def create_db():
    con = psycopg2.connect(dbname='postgres',
        user=DB_USER, host=DB_HOST, port=DB_PORT
        )
    con.autocommit = True
    cursor = con.cursor()
    cursor.execute(f"SELECT COUNT(*) = 0 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    not_exists_row = cursor.fetchone()
    not_exists = not_exists_row[0]
    if not_exists:
        cursor.execute(f'CREATE DATABASE {DB_NAME}')

def connect():
    create_db()
    db.connect()

def create_tables():
    tables = [UserProfile, 
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
