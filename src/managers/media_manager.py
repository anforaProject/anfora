import os
import io
import logging
import magic 
from PIL import Image # Manage images

#import moviepy.editor as mp #Manage videos
mp = 3 #TODO: FIX THIS
from models.status import Status 
from models.user import UserProfile
from models.media import Media 

from settings import (MEDIA_FOLDER, thumb_folder, pic_folder)

logger = logging.getLogger(__name__)


class MediaManager:

    allowed_images = ['image/png', 'image/jpeg']
    allowed_animated = ['image/gif']
    allowed_video = ['video/webm', 'video/mp4']
    allowed = ['image/png', 'image/jpeg', 'image/gif', 'video/webm', 'video/mp4']

    def __init__(self, data):
        self.data = data 

    def is_valid(self):
        mine_type = magic.from_buffer(self.data, mime=True)
        return mine_type in self.allowed


    def store_media(self, filename):
        data = self.data

        #detect the minetype

        mine_type = magic.from_buffer(data, mime=True)
        media_type = 'jpg'
        iobytes = data

        logger.debug(f"Detected media type {mine_type}")

        if mine_type == "image/jpeg":
            media_type = "jpg"
        elif mine_type == 'image/png':
            media_type = 'png'

        if mine_type in self.allowed_images:

            thumb = os.path.join(MEDIA_FOLDER, thumb_folder, filename + f'.thumbnail.{media_type}')
            file_path = os.path.join(MEDIA_FOLDER, pic_folder, filename + f'.{media_type}')

            im = Image.open(io.BytesIO(iobytes))
            if media_type == 'jpg':
                im.save(file_path, 'jpeg', quality=80, optimize=True, progressive=True)
                im.save(thumb, 'jpeg', quality=30, optimize=True, progressive=True)
                return im.size[0], im.size[1], "image/jpeg"
            else:
                im.save(file_path, 'png', optimize=True)
                im.save(thumb, 'png', optimize=True)
                return im.size[0], im.size[1], "image/png"
                
            

        elif mine_type in self.allowed_animated:
            file_path = os.path.join(MEDIA_FOLDER, pic_folder, filename + "_temp" + '.gif')

            with open(file_path, 'wb') as f:
                f.write(data)

            clip = mp.VideoFileClip(file_path)
            
            #video path
            video_path = os.path.join(MEDIA_FOLDER, pic_folder, filename + '.webm')
            clip.write_videofile(video_path, bitrate='25000k')
            video_path = os.path.join(MEDIA_FOLDER, pic_folder, filename + '.mp4')
            clip.write_videofile(video_path, bitrate='25000k')

            #remove temp file

            os.remove(os.path.join(MEDIA_FOLDER, pic_folder, filename + "_temp" + '.gif'))
            return 1, 1, 'video/mp4'

        elif mine_type in self.allowed_video:

            file_path = os.path.join(MEDIA_FOLDER, pic_folder, filename + "_temp")
            with open(file_path, 'wb') as f:
                f.write(data)

            clip = mp.VideoFileClip(file_path)  
            video_path = os.path.join(MEDIA_FOLDER, pic_folder, filename + '.webm')
            clip.write_videofile(video_path, bitrate='25000k')
            video_path = os.path.join(MEDIA_FOLDER, pic_folder, filename + '.mp4')
            clip.write_videofile(video_path, bitrate='25000k')

            return 1,1,'video/mp4'

        else:

            return False, False, False