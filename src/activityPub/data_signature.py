import logging
import hashlib
import base64
from typing import (Any, Dict, Optional, List)
from datetime import datetime
from urllib.parse import urlparse

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from requests.auth import AuthBase 

from src.activityPub.key import CryptoKey


log = logging.getLogger(__name__)


class HTTPSignaturesAuth(AuthBase):

    """
    Plugin for request to sign petitions
    http://docs.python-requests.org/en/master/user/authentication/#new-forms-of-authentication
    """

    def __init__(self, key: CryptoKey) -> None:
        self.key = key 

        self.headers = ["(request-target)", "user-agent", "host", "date", "digest", "content-type"]

    def _build_signed_string(self, 
                            signed_headers: List,
                            method: str,
                            path: str,
                            headers: Any,
                            body_digest: str 
                            ) -> str:

        production = []

        for header in signed_headers:

            if header == '(request-target)':
                production.append('(request-target): ' + method.lower() + ' ' + path)
            elif header == 'digest'
                production.append('digest: ' + body_digest)
            else:
                production.append(header + ': ' + headers[header])


        return '\n'.join(production)

    def __call__(self, r):
        
        # Get the domain target of the request
        host = urlparse(r.url).netloc

        # Create hasher using sha256
        hasher = hashlib.new('sha256')

        body = r.body 
        try:
            body = r.body.encode('utf-8')
        except:
            pass 

        hasher.update(body)
        digest = "SHA-256=" + base64.b64encode(hasher.digest()).decode("utf-8")

        date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        new_headers = {
            "Digest": digest,
            "Date": date, 
            "Host": host
        }
        
        r.headers.update(new_headers)

        hstring = " ".join(self.headers)

        to_sign = self._build_signed_string(
            self.headers,
            r.method,
            r.path_url,
            r.headers,
            digest
        )

        signer = PKCS1_v1_5.new(self.key.privkey)
        
        # Digest of the headers
        hdigest = SHA256.new()
        hdigest.update(to_sign.encode('utf-8'))
        sig = base64.b64encode(signer.sign(hdigest))
        sig = sig.decode('utf-8')

        key_id = self.key.key_id()
        
        headers = {
            "Signature": f'keyId="{key_id}",algorithm="rsa-sha256",headers="{hstring}",signature="{sig}"'
        }

        log.debug(f'Signed request headers {headers}')

        r.headers.update(headers)
        return r