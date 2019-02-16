import json 
import logging 
import datetime
import dateutil.parser as dp
from typing import List

from activityPub.activities.objects import Note
from activityPub.activities.verbs import Create
from models.user import UserProfile
from models.status import Status
from anfora_parser.parser import Parser
"""
    The objetive of this submodule is to provide an easy and general
    function to create different activies from modules
"""

def generate_create_note(status: Status, users: List[UserProfile]) -> Create: 

    note = status.to_activitystream()

    for user in users:
        note['cc'].append(user.ap_id)
    
    note['to'] += ['https://mstdn.io/users/yabirgb']

    t = Note(note)

    data = {
        'id': note['id'] + '/activity',
        'type': "Create",
        'actor': note['attributedTo'],
        'published': note['published'],
        'object': t,
    }

    if note.get('to'):
        data['to'] = note['to'] 

    if note.get('cc'):
        data['cc'] = note['cc']

    return Create(data)