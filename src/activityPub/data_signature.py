import logging
import hashlib
import base64
from typing import (Any, Dict, Optional, List)
from datetime import datetime
from urllib.parse import urlparse

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from requests.auth import AuthBase 
from pyld import jsonld

from activityPub.key import CryptoKey


log = logging.getLogger(__name__)

def _build_signed_string(
    signed_headers: str, method: str, path: str, headers: Any, body_digest: str
) -> str:
    out = []

    for signed_header in signed_headers.split(" "):
        if signed_header == "(request-target)":
            out.append("(request-target): " + method.lower() + " " + path)
        elif signed_header == "digest":
            out.append("digest: " + body_digest)
        else:
            out.append(signed_header + ": " + headers[signed_header])
    return "\n".join(out)

def sign_headers(dsf,fdfs,fdff,fdf):
    pass

class HTTPSignaturesAuthRequest(AuthBase):

    """
    Plugin for request to sign petitions
    http://docs.python-requests.org/en/master/user/authentication/#new-forms-of-authentication
    """

    def __init__(self, key: CryptoKey) -> None:
        self.key = key 

        self.headers = "(request-target) user-agent host date digest content-type"



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

        to_sign = _build_signed_string(
            self.headers,
            r.method,
            r.path_url,
            r.headers,
            digest
        )

        #print(to_sign)

        signer = PKCS1_v1_5.new(self.key.privkey)
        
        # Digest of the headers
        hdigest = SHA256.new()
        hdigest.update(to_sign.encode('utf-8'))
        sig = base64.b64encode(signer.sign(hdigest))
        sig = sig.decode('utf-8')

        key_id = self.key.key_id()
        
        headers = {
            "Signature": f'keyId="{key_id}",algorithm="rsa-sha256",headers="{self.headers}",signature="{sig}"'
        }

        log.debug(f'Signed request headers {headers}')

        r.headers.update(headers)
        return r

# Manage RSA signatures 

def _options_hash(doc):
    doc = dict(doc["signature"])
    for k in ["type", "id", "signatureValue"]:
        if k in doc:
            del doc[k]
    doc["@context"] = "https://w3id.org/identity/v1"
    normalized = jsonld.normalize(
        doc, {"algorithm": "URDNA2015", "format": "application/nquads"}
    )
    h = hashlib.new("sha256")
    h.update(normalized.encode("utf-8"))
    return h.hexdigest()


def _doc_hash(doc):
    doc = dict(doc)
    if "signature" in doc:
        del doc["signature"]
    normalized = jsonld.normalize(
        doc, {"algorithm": "URDNA2015", "format": "application/nquads"}
    )
    h = hashlib.new("sha256")
    h.update(normalized.encode("utf-8"))
    return h.hexdigest()

def generate_signature(doc: Dict, key: 'Key'):

    options = {
        'type': 'RsaSignature2017',
        'creator': doc['actor'] + '#main-key',
        'created': datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    }

    doc["signature"] = options 
    to_be_signed = _options_hash(doc) + _doc_hash(doc)
    signer = PKCS1_v1_5.new(key.privkey)
    digest = SHA256.new()
    digest.update(to_be_signed.encode("utf-8"))
    sig = base64.b64encode(signer.sign(digest))
    options["signatureValue"] = sig.decode("utf-8")
    doc["signature"] = options 
