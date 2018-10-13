import json
import logging

import falcon

from models.user import UserProfile, User
from models.followers import FollowerRelation
from activityPub import activities

from hooks.pagination import ap_pagination


logger = logging.getLogger()

class Followers():

    auth = {
        'exempt_methods':['GET']
    }

    @falcon.before(ap_pagination)
    def on_get(self, req, resp, username):
        user = User.get_or_none(username=username)
        
        if user:
            user = user.profile.get()
            page = req.context['pagination']['page']
            default_pagination = req.context['pagination']['default_pagination']
            if page:
                # In this case the page params is given
                info = {
                    'id': req.context['pagination']['id'],
                    'partOf':req.context['pagination']['partOf'],
                }
                followers = [follower.uris.id for follower in user.followers().paginate(page,default_pagination)]
                if followers:
                    info['next'] = req.context['pagination']['next']
                
                
                resp.body=json.dumps(activities.OrderedCollectionPage(followers, **info).to_json(), default=str)
                resp.status = falcon.HTTP_200
            else:
                # We return the 0 page
                info = {
                    'id': req.context['pagination']['id'],
                    'first': f"{req.context['pagination']['partOf']}?page=1",
                }
                resp.body=json.dumps(activities.OrderedCollection(**info).to_json())
                
        else:
            logger.debug(f'User not found {username}. AcitivtyPub/followers')
            raise falcon.HTTPNotFound(decription="User not found") 

class Following():

    auth = {
        'exempt_methods':['GET']
    }

    @falcon.before(ap_pagination)
    def on_get(self, req, resp, username):
        user = User.get_or_none(username=username)
        
        if user:
            user = user.profile.get()
            page = req.context['pagination']['page']
            default_pagination = req.context['pagination']['default_pagination']
            if page:
                # In this case the page params is given
                info = {
                    'id': req.context['pagination']['id'],
                    'partOf':req.context['pagination']['partOf'],
                }
                following = [follower.uris.id for follower in user.following().paginate(page,default_pagination)]
                if followers:
                    info['next'] = req.context['pagination']['next']
                    
                resp.body=json.dumps(activities.OrderedCollectionPage(following, **info).to_json(), default=str)
                resp.status = falcon.HTTP_200
            else:
                # We return the 0 page
                info = {
                    'id': req.context['pagination']['id'],
                    'first': f"{req.context['pagination']['partOf']}?page=1",
                }
                resp.body=json.dumps(activities.OrderedCollection(**info).to_json())
                
        else:
            logger.debug(f'User not found {username}. AcitivtyPub/following')
            raise falcon.HTTPNotFound(decription="User not found") 
