from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    return f"{instance.user.id}/%c"

class Result(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.FileField(
        upload_to=user_directory_path
    )

    def __str__(self):
        return "Result_" + self.id
