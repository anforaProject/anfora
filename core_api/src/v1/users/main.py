from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from starlette.schemas import SchemaGenerator

# db imports 
from tortoise.exceptions import DoesNotExist as TortoiseDoesNotExist
from src.models.users import User, UserProfile

# custom import 

from src.errors import DoesNoExist, ValidationError, UserAlreadyExists
from src.utils import validate_user_creation

from src.forms import NewUser

from src.v1.auth import get_current_user

router = APIRouter()

@router.get('/accounts/{username}')
async def get_user_by_username(username:str):

    """

    Given an username return the stored information about the user
    with the given username

    """
    
    try:
        user = await UserProfile.get(user__username=username)
        return JSONResponse(await user.to_json())
    except TortoiseDoesNotExist: 
        return DoesNoExist()


@router.post('/accounts/create')
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
    except TortoiseDoesNotExist:
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

@router.get('/accounts/{username}/followers')
async def get_followers(username):
    try:
        user = await UserProfile.get(user__username=username)
        return JSONResponse(await user.followers.all())
    except TortoiseDoesNotExist: 
        return DoesNoExist()

@router.get('/accounts/{username}/following')
async def get_followers(username):
    try:
        user = await UserProfile.get(user__username=username)
        return JSONResponse(await user.followers)
    except TortoiseDoesNotExist: 
        return DoesNoExist()


@router.get('/accounts/me')
async def get_current_user_information(current_user:UserProfile = Depends):
    pass
