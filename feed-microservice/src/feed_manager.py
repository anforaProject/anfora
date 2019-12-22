import aioredis
from aioredis import RedisConnection

class FeedManager:

    def __init__(self):

        self.r = None
        self.home_feed = "feed:home:{}"
        self.notification_feed = "feed:notifications:{}"

        self.MAX_AMOUNT_REQUEST = 64

    async def _init(self, host=('redis', 6379)):
        pool = await aioredis.create_pool(host)
        self.r = pool
        
    async def push_to_home(self, user_id:str, status_id:int) -> None:

        """
        Add the status with status_id to the home timeline of the user
        
        """

        feed_name = self.home_feed.format(user_id)
        
        await self.r.zadd(feed_name, {status_id: status_id})
        
        
        
    async def remove_from_home(self, user_id:str, status_id:int) -> None:
        
        feed_name = self.home_feed.format(user_id)
        
        await self.r.zrem(feed_name, status_id)


    async def push_notification(self, user_id:str, notification_id:int) -> None:

        """
        Push a notification to the user's notifications timeline
        """

        timeline_name = self.notification_feed.format(user_id)
        await self.r.zadd(timeline_name, {notification.id: notification.id})

    async def remove_notification(self, user_id:str, notification_id:int) -> None:
        
        timeline_name = self.notification_feed.format(user_id)
        await self.r.zrem(timeline_name, notification_id)

    async def query(self, timeline:int, user_id: str, since_id:str=None, max_id=None, local=True, limit=20):

        if timeline == 'home_feed':
            timeline_name = self.home_feed.format(user_id)
        elif timeline == 'notification_feed':
            timeline_name = self.notification_feed.format(user_id)

        # Limit on the numbr of object retrieved
        
        limit = min(limit, self.MAX_AMOUNT_REQUEST)

        ids = []

        if since_id and not max_id:
            # Search the status
            start = self.r.zrank(timeline_name, since_id)
            
            # If the status is in redis
            if start != None:
                # Return the query
                ids = self.r.zrevrange(timeline_name, start, start+limit)
            else:
                ids = []
                
        elif since_id and max_id:

            start = self.r.zrank(timeline_name, since_id)
            end = self.r.zrank(timeline_name, max_id)

            if start and end:
                ids = self.r.zrevrange(timeline_name, start, min(start+limit, end))
            elif start:
                ids = self.r.zrevrange(timeline_name, start, start+limit)
            elif end:
                ids = self.r.zrevrange(timeline_name, start, min(start+limit, end))
            elif not start and not end:
                ids = []

        elif not since_id and max_id:
            # Search the status
            end = self.r.zrank(timeline_name, max_id)
            
            # If the status is in redis
            if end != None:
                # Return the query
                ids = self.r.zrevrange(timeline_name, 0, min(limit, end))
            else:
                ids = []
        elif not since_id and not max_id:
            ids = self.r.zrevrange(timeline_name, 0, limit)
            
        return ids
