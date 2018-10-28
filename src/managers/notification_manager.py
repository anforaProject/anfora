from models.status import Status 
from models.user import UserProfile
from models.notification import Notification
from models.media import Media

from managers.timeline_manager import TimelineManager


class NotificationManager:

    def __init__(self, user:UserProfile, notification: Notification=None):

        """
        user: The user triggering the notification
        """

        self.user = user
        self.notification = notification

    def _notify_user(self,notification: Notification) -> None:
        """
        Notify the correct user after creating the notification object
        """

        TimelineManager(notification.target).push_notification(notification)

    def create_follow_notification(self, target:UserProfile) -> Notification:

        """
        target: The user receiving the notification
        """

        n = Notification.create(
            target = target,
            user = self.user,
            notification_type = 'follow',
        )

        self._notify_user(n)

        return n

    def create_like_notification(self, status: Status) -> Notification:

        """
        status: The status we are liking (this can ve either a image or a comment)
        """

        n = Notification.create(
            target = status.user,
            user = self.user,
            status = status,
            notification_type = 'like',
        )

        self._notify_user(n)

        return n

    def create_mention_notification(self, user:UserProfile) -> Notification:

        """
        user: The user being mentioned
        """

        n = Notification.create(
            target = user,
            user = self.user,
            notification_type = 'mention'
        )

        self._notify_user(n)

        return n

    def delete(self):
        # Deleting the status should delete likes and all the things depending on it
        remove_status(status)

