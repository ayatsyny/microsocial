# coding=utf-8
from django.db import models
from users.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_link = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.user.email
