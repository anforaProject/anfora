from fastapi import FastAPI

# modules

from health import router as health
from manage_media import router as media
from models import Media
from init_db import register_tortoise


app = FastAPI()

app.include_router(
    health,
    prefix='/api/v1'
)

app.include_router(
    media,
    prefix='/api/v1'
)

register_tortoise(
    app, db_url="sqlite://memory.sql", modules={"models": ["models"]}, generate_schemas=True
)
