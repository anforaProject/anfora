import datetime
import bcrypt

from models.user import UserProfile
from managers.user_manager import new_user
from settings import salt_code



username = input("Enter username: ")
admin = input("Should the user be an admin? [y/n]")

while(admin.lower() != 'y' and admin.lower() != 'n'):
    admin = input("Should the user be an admin? [y/n]")

password = input("Type a password: ")
password2 = input("Repeat the password: ")

while(password != password2):
    password = input("Type a password: ")
    password2 = input("Repeat the password: ")

email = input("Enter a email: ")

new_user(
        username = username, 
        password = password, 
        email = email,
        description= "",
        confirmed=True,
        is_admin = admin,
        is_remote=False,
        is_private=False
    )

print("User created successfuly")