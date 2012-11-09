from django.db import models

from distribution.models import Component


class Package(models.Model):
    name = models.CharField(max_length=64)

    components = models.ManyToManyField(Component)
