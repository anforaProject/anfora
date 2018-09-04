from models.status import Status 
from models.user import UserProfile
from models.like import Like

class StatusManager:

    def __init__(self, id):
        
        """
            id: int - Id of the status representing
        """

        self.status = Status.get_or_none(Status.id == id)

        if not self.status:
            raise ValueError(f'Could not find status with id {id}')


        self.id = id

    def like(self, user)
        """
            user: UserProfile - User liking the status

            Returns True if the action was successful
        """
        Like.create(
            user = user,
            status = self.status,
        )
        Status.update({Status.favourites_count: Status.favourites_count + 1}).where(Status.id == self.id)

        return True

    def create(self, user, caption, sensitive, spoiler, public, remote=False, story=False):
        """
            user: UserProfile - User creating the status
            caption: str - Image caption
            sensitive: bool - Content has something sensitive.
            spoiler: str - Content spoiler text
            public: bool - True if yes

            Returns the created status

        """

        return Status.create (
                    caption = caption,
                    is_public = public,
                    user = user,
                    sensitive = sensitive,
                    remote = remote,
                    is_story = story
                )