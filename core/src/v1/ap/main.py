from fastapi import APIRouter
from starlette.responses import JSONResponse
from starlette.schemas import SchemaGenerator

# db imports

from src.models.users import UserProfile

# custom import

from src.errors import DoesNoExist, ValidationError, UserAlreadyExists

router = APIRouter()


@router.get("/ap/{username}")
async def get_ap_by_username_ap(request):
    username = request.path_params["username"]
    try:
        user = await UserProfile.get(user__username=username)
        print(await user.to_activitystream())
        return JSONResponse(await user.to_activitystream())
    except tortoise.exceptions.DoesNotExist:
        return DoesNoExist()
