import os

import falcon

#Middlewares
#from middleware import RequireJSON
from falcon_multipart.middleware import MultipartMiddleware
from falcon_auth import FalconAuthMiddleware

#Storage classes (Manage db)
from manage_db import connect, create_tables

#Resources
from api.v1.photos import (getPhoto, manageUserPhotos)
from api.v1.albums import (createAlbum, getAlbum, addToAlbum)
from api.v1.user import (authUser, getUser)

from api.v1.activityPub.inbox import (Inbox)
from api.v1.activityPub.outbox import (Outbox)

#Auth
from auth import (auth_backend,loadUser)

#Auth values
auth_middleware = FalconAuthMiddleware(auth_backend)

#URLs
from urls import urls

#Create the app
app = falcon.API(middleware=[
    MultipartMiddleware(),
    auth_middleware
])

#Get env vars

upload_folder = os.getenv('UPLOADS', '/home/yabir/killMe/uploads')

#Routes
app.add_route('/api/v1/accounts/{user}', manageUserPhotos(upload_folder))
app.add_route('/api/v1/accounts/{user}/albums', createAlbum())
app.add_route('/api/v1/accounts/{user}/albums/{album}', getAlbum())
app.add_route('/api/v1/accounts/{user}/albums/{album}/add', addToAlbum())

app.add_route('/api/v1/users/{user}/photos/{pid}', getPhoto())

app.add_route('/api/v1/auth/', authUser())
app.add_route(urls["user"], getUser())
app.add_route(urls["outbox"], Outbox())
app.add_route(urls["inbox"], Inbox())

#Connect to db
connect()
create_tables()
