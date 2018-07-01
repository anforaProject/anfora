import falcon
import requests

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

def sign_request(key, data):
    rsakey = RSA.importKey(key) 
    signer = PKCS1_v1_5.new(rsakey) 
    digest = SHA256.new() 
    digest.update(data) 
    sign = signer.sign(digest) 
    return b64encode(sign)

def get_ap_by_uri(uri):
    #Giving a uri ask server using webfinger
    #What is the AP id of the user

    if uri.startswith("@"):
        uri = uri[1:]
    info = uri.split("@")

    headers = {'Accept': 'application/json'}
    r = requests.get(f'https://{info[1]}/.well-known/webfinger?resource={uri}', headers=headers)

    if r.status_code in  [200]:
        js = r.json()
        # get the url that we want, i.e. the ap id where we can call AP methods
        url_rel = next(filter(lambda x: 'type' in x.keys() and x['type'] == 'application/activity+json', js['links']))
        
        return url_rel['href']
    else:
        return r.text