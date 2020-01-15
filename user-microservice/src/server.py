import os

# starlette inports 
from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.schemas import SchemaGenerator
import uvicorn


# db imports 

from db import User, UserProfile
import tortoise.exceptions
from tortoise.contrib.starlette import register_tortoise
# Modules

from v1.users.main import router as users_router
from v1.ap.main import router as ap_router
# custom import 

from errors import DoesNoExist, ValidationError, UserAlreadyExists
from utils import validate_user_creation

from forms import NewUser

app = FastAPI(
    title="Anfora users' API",
    version="0.0.1",
    debug=True
)

if os.environ.get("ENV", "production") == "testing":
    register_tortoise(
        app,
        db_url="sqlite://testing_db.sql",
        modules={"models": ["db"]},
        generate_schemas=True
    )
else:
    register_tortoise(
        app,
        db_url="sqlite://memory.sql",
        modules={"models": ["db"]},
        generate_schemas=True
    )


@app.get('/api/v1/health')
async def homepage():
    return JSONResponse({'status': 'running'})

@app.route('/mock')
async def moch():
    await User.create(
        username='anforaUser',
        password='shouldBeAHashedPassword',
        email='random@example.com'
    )

    user = await User.get(username='anforaUser')

    prof = UserProfile(
        user_id = user.id
    )

    await prof.save()

    profile = await UserProfile.all()
    prof = await profile[0].to_json()
    print(prof)
    return JSONResponse(prof)

app.include_router(
    users_router,
    prefix='/api/v1'
)

app.include_router(
    ap_router,
    prefix='/api/v1'
)
