import os

from models.status import Status 
from models.user import UserProfile
from models.media import Media 

class MediaManager:

    def __init__(self, image, filename, original):
        self.image = image
        self.filename = filename
        self.type = os.path.splitext(original)[1]