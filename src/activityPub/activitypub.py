import json 
import logging 
from typing import (Dict, Any)
import aiohttp
import requests
from settings import BASE_URL
from models.user import UserProfile
from activityPub.data_signature import generate_signature, sign_headers, HTTPSignaturesAuthRequest
from activityPub.key import CryptoKey

log = logging.getLogger(__name__)


def push_to_remote_actor(target: UserProfile, body: Dict) -> Any:

    """
    Send activity to target inbox
    """

    # Create Key
    k = CryptoKey(body["actor"])
    k.new()
    generate_signature(body, k)

    data = json.dumps(body)
    print(data)

    auth = HTTPSignaturesAuthRequest(k)
    r = requests.post(target.uris.inbox, json=body, auth = auth)
    print(r.status_code)
    #print(r.request.headers)
    #print(r.content)
    if r.status_code < 400:
        return True 

    return False




