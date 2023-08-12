from django.db import models
from django.conf import settings
# Create your models here.


class Tag(models.Model):
    """Tag for filtering recipes. """
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name
