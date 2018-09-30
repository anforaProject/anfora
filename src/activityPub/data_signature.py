import datetime
import json
import re
import hashlib # Used to create sha256 hash of the request body
from urllib.parse import urlparse
import logging

import requests

from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256 
from base64 import b64encode, b64decode

from activityPub.identity_manager import ActivityPubId

from models.user import UserProfile

class LinkedDataSignature:

    def __init__(self, json_file):
        self.json = dict(json_file)

    def sign(self, creator):

        """
        Creator is an instance of User
        """


        options = {
            'type': 'RsaSignature2017',
            'creator': f'{creator.uris.id}#main-key',
            'created': f'{datetime.datetime.utcnow():%d-%b-%YT%H:%M:%SZ}'
        }

        options_dic = dict(options)
        del options_dic['type']

        #Load Key
        rsakey = RSA.importKey(creator.private_key) 
        signer = PKCS1_v1_5.new(rsakey) 
        digest = SHA256.new()

        #Prepare data
        data = dict(self.json).update({'signature': options_dic})
        json_data = json.dumps(data).encode('utf8')
        digest.update(json_data) 

        #sign
        sign = signer.sign(digest) 

        #Return encode version
        signature = b64encode(sign)

        #Update the json object with the signature
        options.update({'signatureValue': signature.decode('utf8')})
        self.json.update({'signature': options})

        return self.json

class SignatureVerification:

    """
    This class objetive is to verify sign of the request following 
    https://tools.ietf.org/html/draft-cavage-http-signatures-08

    Attributes:
        headers: A dict containing the request headers
        path: A str with the path of the request
        method: A str with the request method
    """

    def __init__(self,headers, method, path):
        self.signature_fail_reason = None
        self.signed_request_account = None
        self.REQUEST_TARGET = '(request-target)'

        self.method = method.lower()
        self.path = path
        self.headers = headers 

        self.signature_params=self._check_headers()

    def _split_signature(self):
        raw_signature = self.headers['signature']

        #FIX: add default headers -> date
        signature_params = {}   
        
        #Work with the header string to extract the information
        regex = r'([A-Za-z]+)=\"([^\"]+)\"'

        for element in raw_signature.split(','):
            match = re.match(regex, element)
            if match and len(match.groups()) == 2:
                key, value = match.groups()
                signature_params[key] = value

        return signature_params

    def _check_headers(self):
        #Check if the "Signature header is present"
        if 'signature' not in list(map(str.lower, self.headers.keys())):
            signature_fail_reason = "Request is not signed"
            return False

        signature_params = self._split_signature()
    
        ## Check if the params are valid
        if None in [signature_params.get('keyId'), signature_params.get('signature')]:
            self.signature_fail_reason = "Incompatible request signature"
            return False

        return signature_params

    
    def _build_signed_string(self, headers_list):

        
        headers = []
        
        for header in headers_list:
            string = ""
            if header == self.REQUEST_TARGET:
                string = f'{self.REQUEST_TARGET}: {self.method} {self.path}'
            else:
                string = f'{header}: {self.headers.get(header)}'
            headers.append(string)

            
        return '\n'.join(headers)

    def verify(self):

        account = ActivityPubId(self.signature_params['keyId']).uri_to_resource(UserProfile)

        if not account:
            self.signature_fail_reason = "Could not retrive account using keyId"
            return 
            
        if self.verify_public_key(account.public_key):
            self.signed_request_account = account
            return True
        else:
            return False

    def verify_public_key(self, key):
        signature_params = self.signature_params

        #Verify using the public key
        signer = PKCS1_v1_5.new(RSA.importKey(key))
        digest = SHA256.new()

        signature = b64decode(signature_params['signature'])
        compare_signed_string = self._build_signed_string(signature_params['headers'])
        digest.update(compare_signed_string.encode('utf-8'))
        if signer.verify(digest, signature):
            #self.signed_request_account = account
            return True
        else:
            self.signature_fail_reason = "Verification failed"
            return False


    def sign(self, user):
        rsakey = RSA.importKey(user.private_key) 
        signer = PKCS1_v1_5.new(rsakey) 
        digest = SHA256.new()

        as_list = list(self.headers.keys())

        headers = self._build_signed_string(as_list)
        digest.update(headers.encode())
        #sign
        sign = signer.sign(digest) 

        #Return encode version
        signature = b64encode(sign)

        header_list = " ".join(self.headers.keys())

        dic = {
            'keyId': f'{user.ap_id}#main-key',
            'algorithm': 'rsa-sha256',
            'headers': " ".join(as_list),
        }

        return ",".join([f'{x}="{dic[x]}"' for x in dic.keys()])