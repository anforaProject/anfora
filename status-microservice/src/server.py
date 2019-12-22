import time
import random

# db imports 

from db import Status, UserProfile
from init_db import register_tortoise
import tortoise.exceptions

from fastapi import Depends, FastAPI, Header, HTTPException

from api.v1 import statuses

# custom import 

from errors import DoesNoExist, ValidationError, UserAlreadyExists
from utils import validate_status_creation, generate_id

app = FastAPI()

register_tortoise(
    app, db_url="sqlite://memory.sql", modules={"models": ["db"]}, generate_schemas=True
)


@app.get("/api/v1/health/")
async def read_users():
    return {'status': 'ok'}


app.include_router(
    statuses.router,
    prefix="/api/v1/statuses",
    tags=["statuses"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)
