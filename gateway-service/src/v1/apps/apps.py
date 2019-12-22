from typing import Union
from datetime import datetime
import secrets
import aiosqlite

DB_NAME='anfora_apps'

CREATE_TABLES = """ CREATE TABLE IF NOT EXISTS apps(
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    redirect_uris text NOT NULL,
    scopes text NOT NULL default 'read:accounts',
    website text,
    created_at text NOT NULL,
    client_id text NOT NULL,
    client_secret text NOT NULL
);"""

INSERT_APP = """ INSER INTO apps(name, redirect_uris, scopes, website, created_at,
client_id, client_secret) values (?,?,?,?,?,?,?);"""

async def create_tables():

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(CREATE_TABLES)
        await db.commit()

async def new_app(name:str, redirec:str, scopes:str, website:Union[str,None]):
    
    async with aiosqlite.connect(DB_NAME) as db:

        ep = datetime(1970,1,1,0,0,0)
        created_at = (datetime.utcnow() - ep).total_seconds()

        id_ = secrets.token_hex(8)
        secret = secrets.token_hex(32)

        await db.execute(INSERT_APP,
                         (name,redirec,scopes,website,created_at,
                          id_, secret))
        
        return id_, secret
