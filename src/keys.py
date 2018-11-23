from Crypto.PublicKey import RSA


KEYS = {
    "actorKeys":{
        "privateKey": ""
    }
}

with open('private_key.pem') as privatefile:
    KEYS["actorKeys"]["privateKey"] = privatefile.read()

with open('pubkey.pem') as privatefile:
    KEYS["actorKeys"]["publicKey"] = privatefile.read()


PRIVKEY = RSA.importKey(KEYS["actorKeys"]["publicKey"])
PUBKEY = PRIVKEY.publickey()

