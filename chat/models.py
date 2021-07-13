from django.db import models
from django.db.models.base import Model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models.fields import related
from datetime import datetime
from django.utils.timezone import now
from django.utils import timezone

# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length=150)
    password = models.CharField(max_length=200)


    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        return super(Group, self).save(*args, **kwargs)

class Chat(models.Model):
    user = models.ForeignKey(User, related_name="chat", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="chat", on_delete=models.CASCADE)
    message = models.TextField(max_length=60000)
    date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self) -> str:
        return self.message


class Member(models.Model):
    user = models.ForeignKey(User, related_name="member", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="member", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.user) 