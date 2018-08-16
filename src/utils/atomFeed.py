import html
import datetime

from settings import DOMAIN

from models.user import UserProfile
from models.status import Status 

def generate_feed(user, max_id = -1):
    limit = 10
    """
    max_id indicates that the new posts should be younger than this value.
    user represents an User in the db 
    """

    base = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:thr="http://purl.org/syndication/thread/1.0" xmlns:activity="http://activitystrea.ms/spec/1.0/" xmlns:poco="http://portablecontacts.net/spec/1.0" xmlns:media="http://purl.org/syndication/atommedia" xmlns:ostatus="http://ostatus.org/schema/1.0" xmlns:mastodon="http://mastodon.social/schema/1.0">
  <id>{atom}</id>
  <title>{username}</title>
  <subtitle>{bio}</subtitle>
  <updated>{update_date}</updated>
  <logo></logo>
  <author>
    <id>{author_url}</id>
    <activity:object-type>http://activitystrea.ms/schema/1.0/person</activity:object-type>
    <uri>{author_url}</uri>
    <name>{author_url}</name>
    <email>{author_acct}</email>
    <summary type="html">{bio}</summary>
    <link rel="alternate" type="text/html" href="{author_url}"/>
    <link rel="avatar" type="image/jpeg" media:width="120" media:height="120" href="{avatar_url}"/>
    <poco:preferredUsername>{username}</poco:preferredUsername>
    <poco:displayName>{name}</poco:displayName>
    <poco:note>{bio}</poco:note>
    <mastodon:scope>public</mastodon:scope>
  </author>
  <link rel="next" href="{next_url}" type="application/atom+xml" />
  <link rel="alternate" type="text/html" href="{author_url}"/>
  <link rel="self" type="application/atom+xml" href="{atom}"/>
"""

    post = """

    <entry>
        <title>New note by {username}</title>
        <link rel="alternate" href="{post_url}" />
        <id>{post_id}</id>
        <summary type="html">
            <![CDATA[{caption}]]></summary>
        <published>{published}</published>
        <updated>{updated}</updated>
    </entry>
"""

    end = """
</feed>
"""
    #https://pleroma.soykaf.com/users/lain/feed.atom?max_id=11598025
    if(max_id != -1):
        photos = (Status
            .select(Status, UserProfile)
            .join(UserProfile)
            .where(
                (Status.user == user) & 
                (Status.id < max_id)
            )
            .order_by(Status.id.desc())
            .limit(limit))
    else:
        photos = (Status
            .select(Status, UserProfile)
            .join(UserProfile)
            .where(
                (Status.user == user)
            )
            .order_by(Status.id.desc())
            .limit(limit))

    user_statuses = user.timeline()
    
    update_date = None
    try:
        update_date = user.timeline().get().created_at
    except:
        update_date = datetime.datetime.now()

    statuses = []

    # Avoid to create multiple times this dict
    user_uris = user.uris

    last_id = 0
    for photo in photos:
        data = {
            "username": user.username,
            "post_url": photo.uris.id,
            "caption": html.escape(photo.caption),
            "published": photo.created_at,
            "updated": photo.updated_at,
            "post_id": photo.uris.id,
            "id": photo.id
        }
        string = post.format(**data)
        statuses.append(string)
        last_id = photo.id
    statuses.append(end)

    user_data = {
        "username": user.username,
        "name": user.name,
        "bio": user.description,
        "author_url": user_uris.id,
        "atom": user_uris.atom,
        "author_acct": 'acct:{}@{}'.format(user.username, DOMAIN),
        "next_url": user_uris.atom + "?max_id=" + str(last_id),
        "update_date": update_date,
        "avatar_url": user_uris.avatar
    }

    return base.format(**user_data) + '\n'.join(statuses)