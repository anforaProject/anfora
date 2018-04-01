import falcon
from middleware import RequireJSON
from storage import *

from photos import PhotoResource

app = falcon.API(middleware=[
    RequireJSON(),
])

app.add_route('/{pid}/photos', PhotoResource())

connect()
create_tables()
