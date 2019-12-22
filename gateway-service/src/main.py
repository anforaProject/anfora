from fastapi import FastAPI
from v1.users import users
from v1.auth import core as auth

app = FastAPI()

app.include_router(
    users.router,
    prefix='/api/v1'
)

app.include_router(
    auth.router,
    prefix='/api/v1',
)
