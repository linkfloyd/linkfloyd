from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from links.models import Language
from links.models import SITE_RATINGS

class UserPreferences(models.Model):
    user = models.ForeignKey(User)
    known_languages = models.ManyToManyField(Language)
    max_rating = models.PositiveIntegerField(
        verbose_name = "Maximum Rating",
        choices=SITE_RATINGS,
        help_text="how much can you handle?",
        default=1
    )
    def __unicode__(self):
        return "Preferences of %s" % self.user

def create_preferences(sender, instance, created, **kwargs):
    if created and UserPreferences.objects.filter(\
        user__username=instance.username).count() == 0:
        preferences = UserPreferences.objects.create(
            user=instance,
            max_rating=1)
        preferences.known_languages.add(1, 2)

post_save.connect(create_preferences, sender=User)