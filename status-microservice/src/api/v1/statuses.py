from typing import Union

from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK
from starlette.responses import JSONResponse
import tortoise.exceptions

from db import Status, Media
from client import aio
from errors import DoesNoExist, ValidationError, MediaError, ServerError
from api.v1.validation import NewStatus

router = APIRouter()


media_server = f"http://localhost:{os.environ.get('media_port')}/api/v1"

@router.get("/{_id}")
async def get_status_by_id(_id):
    try:
        obj = await Status.get(id=_id)
        data = await obj.to_json()
        return JSONResponse(status_code = HTTP_201_CREATED, content=json)
    except tortoise.exceptions.DoesNotExist:
        return DoesNoExist()

@router.post("/")
async def create_status(user_id:Union[None, int], remote:bool, data:dict):

    # Load data
    
    try:
        ns = NewStatus(**data)
    except:
        ValidationError()

    # check that media files are available

    check_media = await aio.post(f'{meedia_server}/check', data={'media_ids': ns.media_ids})

    r_status = check_media.status

    if r_status == HTTP_200_OK:
        content = await check_media.json()
        if content['status'] != 'ok':
            return MediaError()
    else:
        return ServerError()

    # get the user making the request

    user = await User.get(id = user_id)
    
    # create new status

    try:
        status = await Status.create(
            caption = ns.status,
            spoiler_text = ns.spoiler_text,
            is_public = ns.visibility,
            user = user,
            sensitive = ns.sensitive,
            remote = remote,
            in_reply_to=ns.in_reply_to_id
        )
    except:
        return 
    # store new status media

    obs = []
    
    for media in ns.media_ids:

        media = await Media(id=media)
        obs.append(media)

    status.media_files.add(*obs)
    # send request to feeds

    

    # send job to spread over AP network
