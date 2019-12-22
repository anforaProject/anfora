import os

from fastapi import APIRouter
from v1.client import aio
from v1.utils import pipe_request

from starlette.responses import JSONResponse

router = APIRouter()

user_server = f"http://localhost:{os.environ.get('users_port')}/api/v1"

@router.get("/accounts/{id}")
async def retrive_user(id:str, response:JSONResponse):

    request = await aio.get(f'{user_server}/users/{id}')
    response = await pipe_request(request, response)

    return response
    

@router.get("/accounts/{id}/followers")
async def retrive_user_followers(id:str, response:JSONResponse, limit:int=40):

    params = {'limit':limit}
    
    request = await aio.get(f'{user_server}/users/{id}/followers',
                            params = params)
    json = await request.json()

    return json

@router.get("/accounts/{id}/following")
async def retrive_user_following(id:str, response:JSONResponse, limit:int=40):

    params = {'limit':limit}

    request = await aio.get(f'{user_server}/users/{id}/following',
                            params = params)
    json = await request.json()

    return json

@router.get("/accounts/{id}/statuses")
async def retrive_user_statuses(id:str, response:JSONResponse, limit:int=40):

    params = {'limit':limit}

    request = await aio.get(f'{user_server}/users/{id}/statuses',
                            params = params)
    json = await request.json()

    return json
