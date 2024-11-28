from typing import Any
from django.db import models
from accounts.models import CustomUser

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField(max_length=300)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title