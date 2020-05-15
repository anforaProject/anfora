from fastapi import APIRouter
from starlette.responses import JSONResponse
from starlette.schemas import SchemaGenerator

# db imports
from tortoise.exceptions import DoesNotExist as TortoiseDoesNotExist
from src.models.users import UserProfile

# custom import

from src.errors import DoesNoExist, ValidationError, UserAlreadyExists
from src.utils import validate_user_creation

from src.forms import NewUser

from src.v1.users.main import router


@router.get("/accounts/{username}")
async def get_user_by_username(username):
    try:
        user = await UserProfile.get(user__username=username)
        return JSONResponse(user.to_json())
    except TortoiseDoesNotExist:
        return DoesNoExist()
