from django.db import models
from django.conf import settings
from datetime import datetime

from recipe import models as recipe_models
# Create your models here.

class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        )
    recipe = models.ForeignKey(recipe_models.Recipe,on_delete=models.CASCADE)
    text =  models.TextField()
    created_at = models.DateTimeField(default=datetime.now)