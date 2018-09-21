import argon2
import bcrypt
from argon2.exceptions import VerificationError, VerifyMismatchError
from falcon_auth import TokenAuthBackend, JWTAuthBackend

from models.user import UserProfile, User
from models.token import Token


class Argon2(object):
    '''
    Argon2 class container for password hashing and checking logic using
    argon2, of course. This class may be used to intialize your Flask app
    object. The purpose is to provide a simple interface for overriding
    Werkzeug's built-in password hashing utilities.
    Although such methods are not actually overriden, the API is intentionally
    made similar so that existing applications which make use of the previous
    hashing functions might be easily adapted to the stronger facility of
    argon2.
    To get started you will wrap your application's app object something like
    this::
        app = Flask(__name__)
        argon2 = Argon2(app)
    Now the two primary utility methods are exposed via this object, `argon2`.
    So in the context of the application, important data, such as passwords,
    could be hashed using this syntax::
        password = 'hunter2'
        pw_hash = argon2.generate_password_hash(password)
    Once hashed, the value is irreversible. However in the case of validating
    logins a simple hashing of candidate password and subsequent comparison.
    Importantly a comparison should be done in constant time. This helps
    prevent timing attacks. A simple utility method is provided for this::
        candidate = 'secret'
        argon2.check_password_hash(pw_hash, candidate)
    If both the candidate and the existing password hash are a match
    `check_password_hash` returns True. Otherwise, it returns False.
    .. admonition:: Namespacing Issues
        It's worth noting that if you use the format, `argon2 = Argon2(app)`
        you are effectively overriding the argon2 module. Though it's unlikely
        you would need to access the module outside of the scope of the
        extension be aware that it's overriden.
        Alternatively consider using a different name, such as `flask_argon2
        = Argon2(app)` to prevent naming collisions.
    :param app: The Flask application object. Defaults to None.
    '''

    _time_cost = argon2.DEFAULT_TIME_COST
    _memory_cost = argon2.DEFAULT_MEMORY_COST
    _parallelism = argon2.DEFAULT_PARALLELISM
    _hash_len = argon2.DEFAULT_HASH_LENGTH
    _salt_len = argon2.DEFAULT_RANDOM_SALT_LENGTH
    _encoding = 'utf-8'

    def __init__(self,
                 app=None,
                 time_cost=_time_cost,
                 memory_cost=_memory_cost,
                 parallelism=_parallelism,
                 hash_len=_hash_len,
                 salt_len=_salt_len,
                 encoding=_encoding):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.hash_len = hash_len
        self.salt_len = salt_len
        self.encoding = encoding
        self.ph = argon2.PasswordHasher(self.time_cost,
                                        self.memory_cost,
                                        self.parallelism,
                                        self.hash_len,
                                        self.salt_len,
                                        self.encoding)

    def generate_password_hash(self, password):
        '''Generates a password hash using argon2.
        Example usage of :class:`generate_password_hash` might look something
        like this::
            pw_hash = argon2.generate_password_hash('secret')
        :param password: The password to be hashed.
        '''

        if not password:
            raise ValueError('Password must be non-empty.')

        # if PY3:
        #     if isinstance(password, str):
        #         password = bytes(password, 'utf-8')
        # else:
        #     if isinstance(password, unicode):
        #         password = password.encode('utf-8')

        return self.ph.hash(password)

    def check_password_hash(self, pw_hash, password):
        '''Tests a password hash against a candidate password. The candidate
        password is first hashed and then subsequently compared in constant
        time to the existing hash. This will either return `True` or `False`.
        Example usage of :class:`check_password_hash` would look something
        like this::
            pw_hash = argon2.generate_password_hash('secret')
            argon2.check_password_hash(pw_hash, 'secret') # returns True
        :param pw_hash: The hash to be compared against.
        :param password: The password to compare.
        '''

        try:
            return self.ph.verify(pw_hash, password)
        except VerifyMismatchError:
            return False

def loadUserPass(username, password):
    candidate = User.get_or_none(username=username)
    if candidate != None:
        if bcrypt.hashpw(password,candidate.password):
            return candidate.profile.get()
        else:
            raise falcon.HTTPUnauthorized(
                title='401 Unauthorized',
                description='Invalid user or token missing',
                challenges=None)

def loadUser(payload):
    candidate = User.get_or_none(username=payload['user']['username'])
    if candidate:
        return candidate.profile.get()
    else:
        raise falcon.HTTPUnauthorized(
            title='401 Unauthorized',
            description='Invalid user or token missing',
            challenges=None)


def loadUserToken(token):
    candidate = Token.get_or_none(key=token)
    
    if candidate:
        return candidate.user
    else:
        return None

auth_backend = TokenAuthBackend(loadUserToken,auth_header_prefix="Bearer")
#auth_backend = JWTAuthBackend(loadUser, "GUESSWHAT?THISISNOTSECRET")

def try_logged_jwt(backend, req, resp, resource=None):
    if req.get_header('Authorization'):
        return backend.authenticate(req, resp, resource)
    else:
        return None
