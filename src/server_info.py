from manage_db import connect

from models.followers import FollowerRelation
from models.user import User

connect()
a = FollowerRelation.select()

print("Follows:")
for u in a:
    print(u)
print("====================")
print("Users:")
for u in User.select():
    print(u.username, " con ap_id ", str(u.ap_id))
print("====================")
