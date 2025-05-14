from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class FacebookToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Token for {self.user.username}"

class FacebookPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    access_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'page_id')

    def __str__(self):
        return f"{self.name} ({self.page_id})"
