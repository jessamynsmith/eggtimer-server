from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse
from django.db import models


class UserProfile(models.Model):

    user = models.OneToOneField(auth_models.User)

    def __unicode__(self):
        return "%s (%s)" % (self.user.username, self.full_name)

    def get_absolute_url(self):
        return reverse('profile_detail', args=[self.pk])

    @property
    def full_name(self):
        return self.user.get_full_name()
