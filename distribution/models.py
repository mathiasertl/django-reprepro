from django.db import models

from constants import *

VENDORS = (
    (VENDOR_DEBIAN, 'Debian'),
    (VENDOR_UBUNTU, 'Ubuntu'),
)

class Component(models.Model):
    name = models.CharField(max_length=16)

    def __unicode__(self):
        return self.name

class Distribution(models.Model):
    name = models.CharField(max_length=16)
    vendor = models.SmallIntegerField(choices=VENDORS)

    components = models.ManyToManyField(Component)

    def __unicode__(self):
        return self.name
