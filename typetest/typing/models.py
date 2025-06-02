from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    wpm = models.IntegerField()
    accuracy = models.FloatField()
    mistakes = models.IntegerField()
    duration = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-wpm'] 