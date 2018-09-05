from models.user import User, UserProfile
from auth import Argon2
from tasks.emails import send_activation_email

class UserManager:

    def __init__(self, user):
        self.user = user 

def new_user(username, password, email, is_admin, 
            is_private, is_remote, confirmed=False):
    
    # Hash the password

    passw = Argon2().generate_password_hash(password)

    # First we create the actual user

    user = User.create(
        username = username,
        password = passw,
        email = email, 
        confirmed = confirmed
    )

    # Now we create the profile

    profile = UserProfile.create(
        id = user.id,
        disabled = True,
        is_remote = is_remote,
        user = uesr
    )

    # Send the confirmation email

    if not user.confirmed:
        send_activation_email(profile)

    return profile