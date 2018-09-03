from models.user import UserProfile
from auth import Argon2
import datetime

username = input("Enter username: ")
name = input("Enter a name to display: ")

admin = input("Should the user be an admin? [y/n]")

while(admin.lower() != 'y' and admin.lower() != 'n'):
    admin = input("Should the user be an admin? [y/n]")

password = input("Type a password: ")
password2 = input("Repeat the password: ")

while(password != password2):
    password = input("Type a password: ")
    password2 = input("Repeat the password: ")

email = input("Enter a email: ")

passw = Argon2().generate_password_hash(password)

UserProfile.create(
            username=username,
            password=passw,
            name=name,
            email=email,
            confirmation_sent_at=datetime.datetime.now(),
            last_sign_in_at=1,
            is_admin=admin
        )

print("User created successfuly")