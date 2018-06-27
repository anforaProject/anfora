import os

import falcon

#Middlewares
#from middleware import RequireJSON
from falcon_multipart.middleware import MultipartMiddleware
from falcon_auth import FalconAuthMiddleware
from falcon_cors import CORS

from middleware import (PeeweeConnectionMiddleware, CorsMiddleware)

#Resources
from api.v1.photos import (getPhoto, manageUserPhotos)
from api.v1.albums import (createAlbum, getAlbum, addToAlbum)
from api.v1.user import (authUser, getUser, getFollowers, logoutUser,
                            getStatuses, homeTimeline, atomFeed)

from api.v1.activityPub.inbox import (Inbox)
from api.v1.activityPub.outbox import (Outbox)
from api.v1.activityPub.followers import (Followers)

from api.v1.server import (wellknownNodeinfo, wellknownWebfinger, nodeinfo)

#Auth
from auth import (auth_backend,loadUser)

cors = CORS(allow_origins_list=['*'],
            allow_all_methods=True,
            allow_all_origins=True,
            allow_all_headers=True
            )

#Auth values
auth_middleware = FalconAuthMiddleware(auth_backend,exempt_methods=['OPTIONS'])

#URLs
from urls import urls

from api.v1.server import serverInfo

#Create the app
app = falcon.API(middleware=[
    cors.middleware,
    auth_middleware,
    PeeweeConnectionMiddleware(),

    MultipartMiddleware(),
])

#Get env vars

upload_folder = os.getenv('UPLOADS', '/home/yabir/killMe/uploads')

#Routes
app.add_route('/info', serverInfo())

app.add_route('/api/v1/accounts/{username}', getUser())
app.add_route('/api/v1/accounts/{username}/statuses', getStatuses())
app.add_route('/api/v1/accounts/{username}/followers', getFollowers())
app.add_route('/api/v1/statuses', manageUserPhotos(upload_folder))

app.add_route('/api/v1/auth/', authUser())

app.add_route('/api/v1/timelines/home', homeTimeline())


app.add_route('/.well-known/nodeinfo', wellknownNodeinfo())
app.add_route('/.well-known/webfinger', wellknownWebfinger())
app.add_route('/nodeinfo', nodeinfo())

#User oubox/inbox
app.add_route(urls["outbox"], Outbox())
app.add_route(urls["inbox"], Inbox())

app.add_route(urls["user"], getUser())
app.add_route(urls["atom"], atomFeed())

app.add_route(urls["followers"], Followers())
app.add_route(urls["logout"], logoutUser())
