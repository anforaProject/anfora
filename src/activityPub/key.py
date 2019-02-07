import base64
from typing import (Any, Dict, Optional)

from Crypto.PublicKey import RSA
from Crypto.Util import number

from database import DATABASE
from keys import import_keys


class CryptoKey:

    DEFAULT_KEY_SIZE = 2048
    
    def __init__(self, owner: str, id_: Optional[str]=None) -> None:
        self.owner = owner
        self.privkey_pem: Optional[str] = None
        self.pubkey_pem: Optional[str] = None
        self.privkey: Optional[Any] = None 
        self.pubkey: Optional[Any] = None
        self.id_ = id_ 

    def new(self) -> None:
        self.load(import_keys()["actorKeys"]["privateKey"])

    def key_id(self) -> str:
        return f'{self.owner}#main-key'
    
    def load_pub(self, pubkey_pem: str) -> None:
        self.pubkey_pem = pubkey_pem
        self.pubkey = RSA.importKey(pubkey_pem)

    def load(self, privkey_pem: str) -> None:
        self.privkey_pem = privkey_pem
        self.privkey = RSA.importKey(self.privkey_pem)
        self.pubkey_pem = self.privkey.publickey().exportKey("PEM").decode("utf-8")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.key_id(),
            "owner": self.owner,
            "publicKeyPem": self.pubkey_pem,
        }

    @classmethod
    def from_dict(cls, data):
        try:
            k = cls(data["owner"], data["id"])
            k.load_pub(data["publicKeyPem"])
        except KeyError:
            raise ValueError(f"bad key data {data!r}")
        return k

    def to_magic_key(self) -> str:
        mod = base64.urlsafe_b64encode(
            number.long_to_bytes(self.privkey.n)  # type: ignore
        ).decode("utf-8")
        pubexp = base64.urlsafe_b64encode(
            number.long_to_bytes(self.privkey.e)  # type: ignore
        ).decode("utf-8")
        return f"data:application/magic-public-key,RSA.{mod}.{pubexp}"