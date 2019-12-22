from typing import Optional, List, Union
from datetime import datetime

from pydantic import BaseModel

class Poll(BaseModel):

    options: List[str]
    expires_in: int
    multiple: Optional[bool]
    hide_totals: Optional[bool]

class NewStatus(BaseModel):

    status: Union[str, None] = None
    in_reply_to_id: Optional[int] = None
    media_ids: List[int]
    poll: Optional[Poll] = None 
    sensitive: Optional[bool] = False
    spoiler_text: Optional[str] = ''
    visibility: Optional[str] = 'public' 
    scheduled_at: datetime = datime.utcnow().isoformat()
    language: Optional[str] = 'eng'
    
