import os

import falcon

#Middlewares
from middleware import RequireJSON
from falcon_multipart.middleware import MultipartMiddleware

#Storage classes (Manage db)
from storage import *

#Resources
from photos import (getPhoto, addPhoto)

#Create the app
app = falcon.API(middleware=[
    MultipartMiddleware(),
])

#Get env vars

upload_folder = os.getenv('UPLOADS', '/home/yabir/killMe/uploads')

#Add route
app.add_route('/photos/', addPhoto(upload_folder))
app.add_route('/photos/{pid}', getPhoto())

#Connect to db
connect()
create_tables()
