from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Custom fields (optional)
    bio = models.TextField(blank=True, null=True)


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    c_code = models.TextField()
    rust_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"