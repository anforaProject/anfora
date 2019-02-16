import json 
import logging 
from typing import (Dict, Any, Union)
import aiohttp
import requests
from settings import BASE_URL
from models.user import UserProfile
from activityPub.data_signature import generate_signature, sign_headers, HTTPSignaturesAuthRequest
from activityPub.key import CryptoKey

log = logging.getLogger(__name__)


def push_to_remote_actor(target: Union[UserProfile, str], body: Dict) -> Any:

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

    # We need this disjuntion because in the case of shared inbox
    # in the db I store them as a string and not as an object
    # maybe would be cool to model this as a relation between an 
    # instance and an user but ... this is how it's now

    typed_target = target

    if type(target) == UserProfile:
        typed_target = target.uris.inbox

    
    headers = {
        'Content-Type': 'application/activity+json'
    }


    r = requests.post(typed_target, json=body, headers = headers, auth = auth)

    print("=====================================")
    print(typed_target)
    print(r.status_code)
    print(r.request.headers)
    print(r.content)
    print("=====================================")
    if r.status_code < 400:
        return True 
    else:
        log.error(f"Error sending:\n {body} \nto: {typed_target}\nRESPONSE:{r.content}")
        
    return False




