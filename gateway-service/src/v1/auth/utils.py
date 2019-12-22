from datetime import datetime, timedelta
import os
from typing import Dict

import jwt
from passlib.context import CryptContext

from v1.client import aio

SECRET = os.environ.get('SECRET_ANFORA', 'keepthisverysecret')
ALGORITHM = "HS512"

def create_access_token(data:Dict, exp_delta:timedelta=None):

    to_encode = data.copy()

    if exp_delta:
        expire = datetime.utcnow() + exp_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({'exp':expire})

    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt
    
