from manage_db import connect

from models.followers import FollowerRelation
from models.user import User
from models.photo import Photo

connect()
a = FollowerRelation.select()

print("Follows:")
for u in a:
    print(u)
print("====================")
print("Users:")
for u in User.select():
    print(u.username, " con ap_id ", str(u.ap_id))
    print(list(u.statuses()))
    print("----")
print("====================")
print(User.select().count())
print("========")
print("Photos")
for p in Photo.select():
    print(p)

print("========")
print("Following test:")
t = User.get(username="test")
print(t.followers().count())
