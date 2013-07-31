from django.db import models

from distribution.models import Component


class Package(models.Model):
    name = models.CharField(max_length=64, unique=True)
    all_components = models.BooleanField(default=False)

    components = models.ManyToManyField(Component)

    # Very useful if binary packages have individual changelogs where
    # the version is different from the source package version.
    remove_on_update = models.BooleanField(
        default=False,
        help_text="Remove package from index prior to adding a new version of the package."
    )

    def __unicode__(self):
        return self.name
