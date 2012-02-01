from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class Channel(models.Model):
    """Channel model for linkfloyd.

    Users can be members or admins of channels. If an user is admin of channel
    """

    name = models.CharField(verbose_name=_("title"), max_length=255, unique=True)
    slug = models.SlugField(verbose_name=_("slug"), max_length=255, unique=True)
    description = models.TextField(verbose_name=_("description"))
    is_official = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/links/channel/%s/" % self.slug

class Subscription(models.Model):
    user = models.ForeignKey(User)
    channel = models.ForeignKey(Channel)

    status = models.CharField(
        max_length=12,
        default="member",
        choices=(("member", "Member"),
                 ("admin", "Admin")))

    email_frequency = models.CharField(
        max_length=12,
        default="weekly",
        choices=(("daily", "daily"),
                 ("weekly", "Weekly"),
                 ("noemail", "No Email")))
    def __unicode__(self):
        return "%s's subscription to %s as %s" % (self.user,
                                                  self.channel,
                                                  self.status)