from django.db import models
from django.conf import settings


# Create your models here.


class Recipe(models.Model):
    """Recipe Object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='recipes',null=True,blank=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    ingredients = models.JSONField()
    tags = models.ManyToManyField('tags.Tag',blank=True,null=True)

    def __str__(self):
        return self.title
