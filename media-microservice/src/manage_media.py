import os
import asyncio
import traceback
import sys
import uuid
from typing import List, Dict


from fastapi import APIRouter, File, UploadFile, Form
import aiofiles

from models import Media


router = APIRouter()

media_path = os.getenv("MEDIA_PATH")
uploads_folder = os.getenv("UPLOAD_FOLDER")

@router.post("/media")
async def new_media(user_id:str=Form(...), description:str=Form(...),
                    focusx:str=Form(...), focusy:str=Form(...),
                    file: UploadFile = File(...)):


    focusx, focusy = float(focusx), float(focusy)

    pid = uuid.uuid4()
    ftype = file.content_type.split('/')[1]
    path = os.path.join(media_path,uploads_folder,f'{str(pid)}.{ftype}')
    
    async with aiofiles.open(path, 'wb') as f:
        await f.write(await file.read())
    
    try:
        media = Media(mid = pid,
                      user = user_id,
                      description = description,
                      focusx = focusx,
                      focusy = focusy,
                      extension = ftype,
        )

        await media.save()
        
        return media.to_json()

    except Exception:
        traceback.print_exc(file=sys.stdout)
        os.remove(path)

