from Crypto.PublicKey import RSA


def import_keys():

    KEYS = {
        "actorKeys":{
            "privateKey": ""
        }
    }

    with open('private_key.pem') as privatefile:
        KEYS["actorKeys"]["privateKey"] = privatefile.read()

    with open('pubkey.pem') as privatefile:
        KEYS["actorKeys"]["publicKey"] = privatefile.read()

    return KEYS
