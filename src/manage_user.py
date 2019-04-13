import datetime
import bcrypt

from models.user import UserProfile
from managers.user_manager import new_user
from settings import salt_code

def create_user(username='config/docker.yaml', password='settings.py', email='settings.py', is_admin='settings.py'):
    
new_user(
        username = username, 
        password = password, 
        email = email,
        description= "",
        confirmed=True,
        is_admin = admin,
        is_remote=False,
        is_private=False
    )