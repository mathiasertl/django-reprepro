from django.db import models

class IncomingDirectory(models.Model):
    location = models.CharField(max_length=64)
    enabled = models.BooleanField(default=True)
