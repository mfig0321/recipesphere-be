from django.db import models
from django.contrib.auth import (
    get_user_model,
    authenticate,
)

import os

class Profile(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6)
    favorites = models.ManyToManyField('recipe.Recipe')

