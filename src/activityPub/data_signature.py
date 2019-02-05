import aiohttp
import aiohttp.web
import base64
import logging

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA, SHA256, SHA512
from Crypto.Signature import PKCS1_v1_5

from cachetools import LFUCache
from async_lru import alru_cache

from activityPub.remote_actor import fetch_actor


HASHES = {
    'sha1': SHA,
    'sha256': SHA256,
    'sha512': SHA512
}


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


SIGSTRING_CACHE = LFUCache(1024)

def sign_signing_string(sigstring, key):
    if sigstring in SIGSTRING_CACHE:
        return SIGSTRING_CACHE[sigstring]

    pkcs = PKCS1_v1_5.new(key)
    h = SHA256.new()
    h.update(sigstring.encode('ascii'))
    sigdata = pkcs.sign(h)

    sigdata = base64.b64encode(sigdata)
    SIGSTRING_CACHE[sigstring] = sigdata.decode('ascii')

    return SIGSTRING_CACHE[sigstring]


def sign_headers(headers, key, key_id):
    headers = {x.lower(): y for x, y in headers.items()}
    used_headers = headers.keys()
    sig = {
        'keyId': key_id,
        'algorithm': 'rsa-sha256',
        'headers': ' '.join(used_headers)
    }
    sigstring = build_signing_string(headers, used_headers)
    sig['signature'] = sign_signing_string(sigstring, key)

    chunks = ['{}="{}"'.format(k, v) for k, v in sig.items()]
    return ','.join(chunks)


@alru_cache(maxsize=16384)
async def fetch_actor_key(actor):
    actor_data = await fetch_actor(actor)

    if not actor_data:
        return None

    if 'publicKey' not in actor_data:
        return None

    if 'publicKeyPem' not in actor_data['publicKey']:
        return None

    return RSA.importKey(actor_data['publicKey']['publicKeyPem'])


async def validate(actor, request):
    pubkey = await fetch_actor_key(actor)
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


async def http_signatures_middleware(app, handler):
    async def http_signatures_handler(request):
        request['validated'] = False

        if 'signature' in request.headers:
            data = await request.json()
            if 'actor' not in data:
                raise aiohttp.web.HTTPUnauthorized(body='signature check failed, no actor in message')

            actor = data["actor"]
            if not (await validate(actor, request)):
                logging.info('Signature validation failed for: %r', actor)
                raise aiohttp.web.HTTPUnauthorized(body='signature check failed, signature did not match key')

            return (await handler(request))

        return (await handler(request))

    return http_signatures_handler
