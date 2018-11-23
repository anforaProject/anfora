import datetime
import json
import re
import hashlib # Used to create sha256 hash of the request body
from urllib.parse import urlparse
import logging


import base64
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA, SHA256, SHA512
from Crypto.Signature import PKCS1_v1_5

from activityPub.identity_manager import ActivityPubId

from models.user import UserProfile

def split_signature(sig):
    default = {"headers": "date"}

    sig = sig.strip().split(',')

    for chunk in sig:
        k, _, v = chunk.partition('=')
        v = v.strip('\"')
        default[k] = v

    default['headers'] = default['headers'].split()
    return default


def build_signing_string(headers, used_headers):
    return '\n'.join(map(lambda x: ': '.join([x.lower(), headers[x]]), used_headers))


def sign_headers(headers, key, key_id):
    headers = {x.lower(): y for x, y in headers.items()}
    used_headers = headers.keys()
    sig = {
        'keyId': key_id,
        'algorithm': 'rsa-sha256',
        'headers': ' '.join(used_headers)
    }
    sigstring = build_signing_string(headers, used_headers)

    pkcs = PKCS1_v1_5.new(key)
    h = SHA256.new()
    h.update(sigstring.encode('ascii'))
    sigdata = pkcs.sign(h)

    sigdata = base64.b64encode(sigdata)
    sig['signature'] = sigdata.decode('ascii')

    chunks = ['{}="{}"'.format(k, v) for k, v in sig.items()]
    return ','.join(chunks)


def fetch_actor_key(actor):
    actor_data = fetch_actor(actor)

    if not actor_data:
        return None

    if 'publicKey' not in actor_data:
        return None

    if 'publicKeyPem' not in actor_data['publicKey']:
        return None

    return RSA.importKey(actor_data['publicKey']['publicKeyPem'])


def validate(actor, request):
    pubkey = fetch_actor_key(actor)
    if not pubkey:
        return False

    logging.debug('actor key: %r', pubkey)

    headers = request.headers.copy()
    headers['(request-target)'] = ' '.join([request.method.lower(), request.path])

    sig = split_signature(headers['signature'])
    logging.debug('sigdata: %r', sig)

    sigstring = build_signing_string(headers, sig['headers'])
    logging.debug('sigstring: %r', sigstring)

    sign_alg, _, hash_alg = sig['algorithm'].partition('-')
    logging.debug('sign alg: %r, hash alg: %r', sign_alg, hash_alg)

    sigdata = base64.b64decode(sig['signature'])

    pkcs = PKCS1_v1_5.new(pubkey)
    h = HASHES[hash_alg].new()
    h.update(sigstring.encode('ascii'))
    result = pkcs.verify(h, sigdata)

    request['validated'] = result

    logging.debug('validates? %r', result)
    return result
