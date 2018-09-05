import bcrypt

from settings import salt_code
from models.user import User, UserProfile
from tasks.emails import send_activation_email

class UserManager:

    def __init__(self, user):
        self.user = user 

def new_user(username, password, email,
             is_remote = False, confirmed=False, is_private = False, 
             is_admin=False):
    
    # Hash the password

    passw = bcrypt.hashpw(password, salt_code)

    # First we create the actual user

    user = User.create(
        username = username,
        password = passw,
        email = email, 
        confirmed = confirmed,
        is_admin = is_admin,
        is_private = is_private
    )

    # Now we create the profile

    profile = UserProfile.create(
        id = user.id,
        disabled = True,
        is_remote = is_remote,
        user = user
    )

    # Send the confirmation email

    if not user.confirmed:
        send_activation_email(profile)

    return profile