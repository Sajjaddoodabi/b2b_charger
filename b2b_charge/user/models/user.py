import logging
import os
from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files import File
from django.db import models

logger = logging.getLogger(__name__)


class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True, upload_to="avatars/")


    def __str__(self) -> str:
        return self.username

    def save(self, *args, **kwargs):
        self.full_name = f"{self.first_name} {self.last_name}"

        try:
            if isinstance(self.avatar, bytes):
                username = self.username
                old_file_path = os.path.join(
                    settings.MEDIA_ROOT, f"avatars/{username}.jpg"
                )
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                self.avatar = File(BytesIO(self.avatar), name=f"{username}.jpg")
        except Exception as e:
            logger.error(
                f"ERROR IN USER SAVE: Failed to process avatar for user {self.username}: {e}"
            )
            self.avatar = None

        super(User, self).save(*args, **kwargs)

    @property
    def photo(self):
        avatar_path = os.path.join("media/avatar", f"{self.username}.jpg")
        if os.path.exists(avatar_path):
            return f"{settings.MEDIA_URL}avatar/{self.username}.jpg"
        return f"{settings.MEDIA_URL}avatar/sample_avatar.jpg"
