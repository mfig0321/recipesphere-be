# Generated by Django 4.2.4 on 2023-08-23 23:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='recipes/')),
                ('description', models.TextField(blank=True)),
                ('instructions', models.TextField(blank=True)),
                ('time_minutes', models.IntegerField()),
                ('ingredients', models.JSONField()),
                ('tags', models.ManyToManyField(blank=True, null=True, to='tags.tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
