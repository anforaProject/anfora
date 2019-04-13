import datetime
import bcrypt

from models.user import UserProfile
from managers.user_manager import new_user
from settings import salt_code

def create_user(username, password, email, is_admin=False):
    
    new_user(
            username = username, 
            password = password, 
            email = email,
            description= "",
            confirmed=True,
            is_admin = is_admin,
            is_remote=False,
            is_private=False
        )