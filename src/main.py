import os

import falcon

#Middlewares
from middleware import RequireJSON
from falcon_multipart.middleware import MultipartMiddleware
from falcon_auth import FalconAuthMiddleware

#Storage classes (Manage db)
from storage import *

#Resources
from photos import (getPhoto, addPhoto)
from user import (authUser)

#Auth
from auth import (auth_backend,loadUser)

#Auth values
auth_middleware = FalconAuthMiddleware(auth_backend)

#Create the app
app = falcon.API(middleware=[
    MultipartMiddleware(),
    auth_middleware
])

#Get env vars

upload_folder = os.getenv('UPLOADS', '/home/yabir/killMe/uploads')

#Add route
app.add_route('/photos/', addPhoto(upload_folder))
app.add_route('/photos/{pid}', getPhoto())

app.add_route('/auth/', authUser())

#Connect to db
connect()
create_tables()
