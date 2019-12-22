import asyncio

from fastapi import FastAPI
from feed_manager import FeedManager


app = FastAPI()

# Create an instance of the feed manager
feed_manager = FeedManager()

# Initialize the feed manager
asyncio.ensure_future(feed_manager._init())  # add coro() to be run by event loop without blocking flow here


@app.get("/api/v1/health")
async def v1_health():
    return {"status": "Server running"}

@app.get("/api/v1/homefeed/{user_id}")
async def v1_home_feed(user_id: str):
    return {"user_id": user_id}
