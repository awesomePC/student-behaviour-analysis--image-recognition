from django.db import models

from users.models import CustomUser

# Create your models here.

def user_dataset_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/dataset/user_<id>/<filename>
    return 'dataset/user_{0}/{1}'.format(
        instance.user.id, filename
    )

def user_face_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/face/user_<id>/<filename>
    return 'face/user_{0}/{1}'.format(
        instance.user.id, filename
    )

def user_face_embedding_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/face/user_<id>/<filename>
    return 'face_embedding/user_{0}/{1}'.format(
        instance.user.id, filename
    )


class TempRegistrationImage(models.Model):
    """
    User uploaded images will be stored here
    
    Arguments:
        models {[type]} -- [description]
    """
    lazy_user_id = models.IntegerField(
        help_text="Temp user id",
        blank=True, null=True
    )
    img = models.FileField(
        upload_to="temp/%Y/%m/%d",
        help_text="After successfull user registration move file to dataset folder"
    )
    is_valid = models.BooleanField(default=False)
    more_info = models.TextField(
        blank=True, null=True
    )

class CandidateImgDataset(models.Model):
    """
    User training data will be stored here
    
    Arguments:
        models {[type]} -- [description]
    """
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True
    )
    img = models.FileField(upload_to=user_dataset_directory_path)
    face = models.FileField(upload_to=user_face_directory_path, blank=True, null=True, help_text="face extracted from image by MTCNN face detector")
    face_embedding = models.FileField(upload_to=user_face_embedding_directory_path, blank=True, null=True, help_text="Embedding(feature) extracted by Facenet model in 128d")
    is_valid = models.BooleanField(default=True)
    more_info = models.TextField(
        blank=True, null=True
    )

