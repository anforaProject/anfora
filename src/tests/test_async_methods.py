import pytest

from peewee_async import Manager

from managers.user_manager import new_user_async
from models.base import db
from models.user import User, UserProfile

objects = Manager(db)

@pytest.mark.asyncio
async def test_async_new_user_free():

    try:
        user = await objects.get(UserProfile.select().where(User.email == 'doomyemail6@test.com'))
        await objects.delete(user, recursive=True)
    except:
        pass
        

    res = await new_user_async(
        username = 'veryRandomUsername5',
        password = 'notARandomPassword',
        email = 'doomyemail6@test.com',
        description = "test user",
        send_confirmation = False
    )
    assert res != False
    await objects.delete(res, recursive=True)

@pytest.mark.asyncio
async def test_async_new_user_bad_password():
    res = await new_user_async(
        username = 'veryRandomUsername2',
        email = 'doomyemail@test.com',
        password = None,
        description = "test user",
        send_confirmation = False
    )
    assert res == False