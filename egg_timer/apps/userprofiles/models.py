from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse
from django.db import models


class UserProfile(models.Model):

    user = models.OneToOneField(auth_models.User)
    birth_date = models.DateTimeField(null=True, blank=True)
    luteal_phase_length = models.IntegerField(default=14)

    def __unicode__(self):
        return "%s (%s)" % (self.user.username, self.full_name)

    def get_absolute_url(self):
        return reverse('profile_detail', args=[self.pk])

    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        full_name = self.user.get_full_name()
        if not full_name:
            full_name = self.user.username
        return full_name


def create_userprofile(sender, instance, **kwargs):
    try:
        UserProfile.objects.get(user_id=instance.id)
    except UserProfile.DoesNotExist:
        UserProfile(user=instance).save()
        try:
            group = auth_models.Group.objects.get(name='users')
            group.user_set.add(instance)
            group.save()
        except auth_models.Group.DoesNotExist:
            # TODO when/how to create group?
            pass


models.signals.post_save.connect(create_userprofile, sender=auth_models.User)
