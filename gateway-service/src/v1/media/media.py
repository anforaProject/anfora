import os

from fastapi import APIRouter, File, UploadFile
from v1.client import aio

router = APIRouter()

media_server = f"http://localhost:{os.environ.get('media_port')}/api/v1/media"

class Media(BaseModel):
    user_id: str
    description: str
    focus: str
    
@router.post("/")
async def create_media(id, fil:UploadFile=File(...), media:Media):

    data = {
        'user_id' = media.user_id,
        'description' = media.description,
        'focusx' = float(media.focus.split('.')[0]),
        'focusy' = float(media.focus.split('.')[1]),
        'fil' = fil
    }
    
    request = await aio.post(f'{media_server}', data=data)
    json = await request.text()

    return json
    
