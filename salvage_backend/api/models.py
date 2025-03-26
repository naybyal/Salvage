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
    
class TranslationTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    logs = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TranslationTask {self.id} ({self.file.name})"
    
class TranslationResult(models.Model):
    task = models.OneToOneField('TranslationTask', on_delete=models.CASCADE)
    output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for Task {self.task.id}"

class Analysis(models.Model):
    task = models.ForeignKey(TranslationTask, on_delete=models.CASCADE, related_name="analyses")
    insights = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Task {self.task.id}"
