import bcrypt
import re 

from settings import salt_code
from models.user import User, UserProfile
from tasks.emails import send_activation_email

from models.status import Status 
from models.like import Like

from tasks.redis.spreadStatus import like_status

class UserManager:

    def __init__(self, user):
        self.user = user 

    def like(self, status):
        """
            user: UserProfile - User liking the status

            Returns True if the action was successful
        """

        # Check if the user already liked it

        if Like.get_or_none(user=self.user,status=status):
            return False
        
        # First we create the like object
        Like.create(
            user = self.user,
            status = status,
        )

        # Update the counter in the object
        Status.update({Status.favourites_count: Status.favourites_count + 1}).where(Status.id == status.id)

        # Create a redis notification
        like_status(status, self.user)
        
        return True

    def dislike(self, status):

        # Check if the like exists
        like = Like.get_or_none(user=self.user,status=status)
        if not like:
            return False 
        like.delete().execute()
        Status.update({Status.favourites_count: Status.favourites_count - 1}).where(Status.id == status.id)

def valid_username(username):
    regex = r'[\w\d_.]+$'
    return re.match(regex, username) != None

def new_user(username, password, email,
             is_remote = False, confirmed=False, is_private = False, 
             is_admin=False, public_key=None, name=None, description = None, ap_id = None):

    """
        Returns False or UserProfile
    """
    
    # Verify username

    if not valid_username(username):
        return False

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

    if name == None:
        name = username

    # Now we create the profile

    profile = UserProfile.create(
        id = user.id,
        disabled = True,
        is_remote = is_remote,
        user = user,
        name = name,
        public_key = public_key,
        ap_id = ap_id,
        description = description
    )

    # Send the confirmation email

    if not user.confirmed:
        send_activation_email(profile)

    return profile