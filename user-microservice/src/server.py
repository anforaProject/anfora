# starlette inports 
from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.schemas import SchemaGenerator
import uvicorn


# db imports 

from db import User, UserProfile
from init_db import register_tortoise
import tortoise.exceptions

# custom import 

from errors import DoesNoExist, ValidationError, UserAlreadyExists
from utils import validate_user_creation

from forms import NewUser

app = FastAPI(debug=True)

register_tortoise(
    app, db_url="sqlite://memory.sql", modules={"models": ["db"]}, generate_schemas=True
)


@app.get('/api/v1/health')
async def homepage(request):
    return JSONResponse({'status': 'running'})

@app.route('/mock')
async def moch(request):
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

@app.get('/api/v1/users/{username}')
async def get_user_by_username(username):
    try:
        user = await UserProfile.get(user__username=username)
        return JSONResponse(await user.to_json())
    except tortoise.exceptions.DoesNotExist: 
        return DoesNoExist()

@app.get('/v1/activitypub/{username}')
async def get_ap_by_username_ap(request):
    username = request.path_params['username']
    try:
        user = await UserProfile.get(user__username=username)
        print(await user.to_activitystream())
        return JSONResponse(await user.to_activitystream())
    except tortoise.exceptions.DoesNotExist: 
        return DoesNoExist()


@app.post('/api/v1/users/create')
async def create_new_user(data:dict, response:JSONResponse):

    try:
        data = NewUser(**data)
    except:
        ValidationError()

        # Check that an user with this userma doesn't exists already

    try:
        user = await User.get(username=data.username)
        if user:
            return UserAlreadyExists()
    except tortoise.exceptions.DoesNotExist:
        user = await User.create(
            username=data.username,
            password=data.password,
            email=data.email
        )

        prof = UserProfile(
            user_id = user.id
        )

        await prof.save()

        return JSONResponse(await prof.to_json())
