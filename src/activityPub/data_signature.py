import datetime
import json

from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256 
from base64 import b64encode

class LinkedDataSignature:

    def __init__(self, json):
        self.json = dict(json)

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