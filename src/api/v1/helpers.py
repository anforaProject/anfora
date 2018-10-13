import os

import requests
import redis 
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256 
from base64 import b64encode, b64decode

def its_me(username):

    def hook (req, resp, resource, params):
        
        if req.context['user'].username != params.username:
            raise falcon.HTTPForbidden("You don't have permissions")

    return hook


def max_body(limit):

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook

def sign_data(key, data):

    """
    To update the digest data needs to be a bytes object.
    """

    rsakey = RSA.importKey(key) 
    signer = PKCS1_v1_5.new(rsakey) 
    digest = SHA256.new() 
    digest.update(data) 
    sign = signer.sign(digest) 
    return b64encode(sign)

def get_ap_by_uri(uri):
    #Giving a uri ask server using webfinger
    #What is the AP id of the user

    #Open a connection with redis
    redis_connection = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))

    #Try to search the uri in the redis db

    obj = redis_connection.get(uri)

    #If not None we have a match 
    
    if obj:
        return obj.decode('utf-8')
        
    if uri.startswith("@"):
        uri = uri[1:]
    
    info = uri.split("@")
    
    headers = {'Accept': 'application/json'}
    r = requests.get(f'https://{info[1]}/.well-known/webfinger?resource={uri}', headers=headers)

    if r.status_code in [200]:
        js = r.json()
        # get the url that we want, i.e. the ap id where we can call AP methods
        url_rel = next(filter(lambda x: 'type' in x.keys() and x['type'] == 'application/activity+json', js['links']))
        
        #Before returning the value store it in redis
        redis_connection.set(uri, url_rel['href'], ex=86400)

        return url_rel['href']
    else:
        return r.text
