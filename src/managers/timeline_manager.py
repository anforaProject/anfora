import os
import redis

class TimelineManager:

    def __init__(self, user):

        """
        Manage timelines of one user.

        user: User wich timelines it'll manage
        """

        self.r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
        self.user = user
        
        # Timelines names
        self.HOME_TIMELINE = 'feed:home:{}'
        self.NOTIFICATIONS = 'feed:notifications:{}'

        # Timelines sizes

        self.HOME_TIMELINE_SIZE = 400
        
        # Queries max

        self.MAX_AMOUNT_REQUEST = 50


    def push_home(self, status):
        """
        Push the status id to the hometiles of the timeline user

        status: An instance of Status
        """

        timeline_name = self.HOME_TIMELINE.format(self.user.id)


        self.r.zadd(timeline_name, status.id, status.id)

    def remove_from_home(self, status_id):
        
        """
        id is an integer representating the status id

        
        """
        timeline_name = self.HOME_TIMELINE.format(self.user.id)
        self.r.zrem(timeline_name, status_id)

    def push_notification(self, notification):

        """
        Push a notification to the user's notifications timeline

        notification: an instance of Notification

        """

        timeline_name = self.NOTIFICATIONS.format(self.user.id)
        self.r.zadd(timeline_name, notification.id, notification.id)

    def remove_notification(self, notification_id):
        timeline_name = self.HOME_TIMELINE.format(self.user.id)
        self.r.zrem(timeline_name, notification_id)

    def range_home(self, count=0, offset=0, limit = -1):
        
        timeline_name = self.HOME_TIMELINE.format(self.user.id)

        # Extract a range of timeline

        count = min(count, self.MAX_AMOUNT_REQUEST)

        # If no count is provided we check the offset and the limit
        if count != 0:
            offset = 0
            limit = count
        
        if limit == 1:
            limit = offset
        elif limit > 0:
            limit = offset + limit - 1

        return self.r.zrevrange(timeline_name, offset, limit, score_cast_func=int)

    def query(self, since_id=None, max_id=None, local=True, limit=20):
        
        timeline_name = self.HOME_TIMELINE.format(self.user.id)

        limit = min(limit, 40)
        ids = []
        if since_id and not max_id:
            # Search the status
            start = self.r.zrank(timeline_name, since_id, score_cast_func=int)
            
            # If the status is in redis
            if start != None:
                # Return the query
                ids = self.r.zrevrange(timeline_name, start, start+limit, score_cast_func=int)
            else:
                ids = []
        elif since_id and max_id:

            start = self.r.zrank(timeline_name, since_id, score_cast_func=int)
            end = self.r.zrank(timeline_name, max_id, score_cast_func=int)

            if start and end:
                ids = self.r.zrevrange(timeline_name, start, min(start+limit, end), score_cast_func=int)
            elif start:
                ids = self.r.zrevrange(timeline_name, start, start+limit)
            elif end:
                ids = self.r.zrevrange(timeline_name, start, min(start+limit, end), score_cast_func=int)
            elif not start and not end:
                ids = []

        elif not since_id and max_id:
            # Search the status
            end = self.r.zrank(timeline_name, max_id, score_cast_func=int)
            
            # If the status is in redis
            if start != None:
                # Return the query
                ids = self.r.zrevrange(timeline_name, 0, min(start+limit, end), score_cast_func=int)
            else:
                ids = []
        elif not since_id and not max_id:
            ids = self.r.zrevrange(timeline_name, 0, limit, score_cast_func=int)
            
        return ids