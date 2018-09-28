import os

import falcon

#Middlewares
#from middleware import RequireJSON
from falcon_multipart.middleware import MultipartMiddleware
from falcon_auth import FalconAuthMiddleware
from falcon_cors import CORS

from settings import MEDIA_FOLDER

from middleware import (PeeweeConnectionMiddleware, CorsMiddleware)

#Resources
from api.v1.statuses import (getStatus, manageUserStatuses, favouriteStatus, unfavouriteStatus)
from api.v1.albums import (createAlbum, getAlbum, addToAlbum)
from api.v1.user import (authUser, getUser, getFollowers, logoutUser,
                            getStatuses, atomFeed, followAction, 
                            manageCredentials,verifyCredentials, 
                            followingAccounts, registerUser, userURLConfirmation)

from api.v1.timelines import (homeTimeline)

from api.v1.media import UploadMedia

from api.v1.client import VueClient

from api.v1.activityPub.inbox import (Inbox)
from api.v1.activityPub.outbox import (Outbox)
from api.v1.activityPub.actor import (getActor)
from api.v1.activityPub.followers import (Followers, Following)

from api.v1.server import (wellknownNodeinfo, wellknownWebfinger, nodeinfo, hostMeta)

#Auth
from auth import (auth_backend,loadUser)

#URLs
from urls import urls

from api.v1.server import serverInfo

cors =  CORS(allow_all_origins=True,
            allow_all_methods=True,
            allow_headers_list=['*'],
            log_level='INFO',
        )

#Auth values
auth_middleware = FalconAuthMiddleware(auth_backend,exempt_methods=['OPTIONS'])


#Create the app
app = falcon.API(middleware=[
    #cors.middleware,
    CorsMiddleware(),
    auth_middleware,
    PeeweeConnectionMiddleware(),
    MultipartMiddleware(),
])

#Routes
app.add_route('/info', serverInfo())

app.add_route('/api/v1/accounts/{id}', getUser())
app.add_route('/api/v1/accounts/{id}/statuses', getStatuses())
app.add_route('/api/v1/accounts/{id}/followers', getFollowers())
app.add_route('/api/v1/accounts/{id}/following', followingAccounts())
app.add_route('/api/v1/accounts/update_credentials', manageCredentials())
app.add_route('/api/v1/statuses', manageUserStatuses())
app.add_route('/api/v1/media', UploadMedia())

app.add_route('/api/v1/statuses/{id}', getStatus())
app.add_route('/api/v1/statuses/{id}/favourite', favouriteStatus())
app.add_route('/api/v1/statuses/{id}/unfavourite', unfavouriteStatus())

app.add_route('/api/v1/auth', authUser())
app.add_route('/api/v1/accounts/verify_credentials', verifyCredentials())
app.add_route('/api/v1/timelines/home', homeTimeline())
app.add_route('/api/v1/follows', followAction())

app.add_route('/api/v1/register', registerUser())
app.add_route('/registration/active/{token}', userURLConfirmation())

app.add_route('/.well-known/nodeinfo', wellknownNodeinfo())
app.add_route('/.well-known/webfinger', wellknownWebfinger())
app.add_route('/nodeinfo', nodeinfo())
app.add_route('/.well-known/host-meta', hostMeta())

#User oubox/inbox
app.add_route(urls["outbox"], Outbox())
app.add_route(urls["inbox"], Inbox())

app.add_route(urls["user"], getActor())
app.add_route(urls["atom"], atomFeed())

app.add_route(urls["followers"], Followers())
app.add_route(urls['following'], Following())
app.add_route(urls["logout"], logoutUser())

app.add_sink(VueClient().on_get, prefix='/')
