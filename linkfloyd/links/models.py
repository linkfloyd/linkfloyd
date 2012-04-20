from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from django.db import models
from django.db.models import F
from django.db.models import Sum

from linkfloyd.utils import SumWithDefault
from channels.models import Channel
from channels.models import Subscription as ChannelSubscription

from qhonuskan_votes.models import VotesField

from django.db.models.signals import pre_delete
from django.db.models.signals import post_save
from qhonuskan_votes.models import vote_changed

from django.db.models import Count

from django.dispatch import receiver

SITE_RATINGS = (
    (1, _("Safe Posts (only safe content)")),
    (2, _("Moderate (can contain nudity, rude gestures)")),
    (3, _("Liberal (hell yeah.)")),
)

SITE_LANGUAGES = (
    ("tr", "Turkish"),
    ("en", "English"),
)

class Language(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=16)

    def __unicode__(self):
        return self.name

class Link(models.Model):
    posted_by = models.ForeignKey(User)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(help_text=_("paste url of your link here"))
    title = models.CharField(max_length=144, help_text=_("title of your link"))
    description = models.CharField(max_length=255, null=True, blank=True,
        help_text=_("say something about that link"))
    thumbnail_url = models.URLField(null=True, blank=True)
    rating = models.PositiveIntegerField(
        choices=SITE_RATINGS,
        help_text=_("warn people about your link")
    )
    language = models.ForeignKey(Language)
    votes = VotesField()
    shown = models.PositiveIntegerField(default=0)
    player = models.TextField(null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    is_sponsored = models.BooleanField(default=False)
    channel = models.ForeignKey(Channel)
    vote_score = models.PositiveIntegerField(default=0)
    comment_score = models.PositiveIntegerField(default=0)

    def get_domain(self):
        from urllib2 import urlparse
        return urlparse.urlparse(self.url).hostname

    def get_absolute_url(self):
        return "/links/%s/" % self.id

    def get_full_url(self):
        from django.contrib.sites.models import Site
        return "http://" + \
            Site.objects.get_current().domain + \
            self.get_absolute_url()

    def get_editing_url(self):
        return "/links/edit/%s/" % self.id

    def get_sharing_url(self):
        return "%s?site=%s" % (Site.objects.get_current().domain, self.url)

    def inc_shown(self):
        self.shown += 1
        self.save()

    def __unicode__(self):
        return u"%s by %s" % (self.title, self.posted_by)

class Subscription(models.Model):
    user = models.ForeignKey(User, related_name="link_subscriptions")
    link = models.ForeignKey(Link)

class Report(models.Model):
    reporter = models.ForeignKey(User)
    link = models.ForeignKey(Link)
    reason = models.CharField(
        max_length=16,
        help_text = "why are you reporting this?",
        choices=(
            ("hatespeech", "Contains hate Speech"),
            ("wrong_channel", "Channel is not appropriate"),
            ("wrong_rating", "Rating is not appropriate"),
            ("wrong_language", "Language is not appropriate"),
            ("other", "Other")
        )
    )
    note = models.CharField(
        max_length=255,
        help_text="do you have note for admins?",
        null=True,
        blank=True
    )
    reported_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def get_link_url(self):
        return self.link.get_absolute_url()

    def __unicode__(self):
        return "%s's report for %s" % (self.reporter, self.reason)


@receiver(post_save, sender=Link, dispatch_uid="link_saved")
def link_saved(sender, **kwargs):

    from summaries.models import Unseen

    if kwargs['created'] == True:
        link = kwargs['instance']
        subscriptions = ChannelSubscription.objects.filter(channel=link.channel)
        for subscription in subscriptions:
            Unseen.objects.get_or_create(user=subscription.user, link=link)
        del(subscriptions)

        LinkSubscription = Subscription
        LinkSubscription.objects.get_or_create(link=link, user=link.posted_by)


@receiver(pre_delete, sender=Link, dispatch_uid="link_deleted")
def link_deleted(sender, **kwargs):
    from summaries.models import Unseen
    link = kwargs['instance']
    Unseen.objects.filter(link=link).delete()

@receiver(vote_changed)
def update_vote_score(sender, dispatch_uid="update_vote_score", **kwargs):
    from qhonuskan_votes.utils import get_vote_model
    link = sender.object
    link.vote_score = link.votes.aggregate(score=Sum('value'))['score']
    link.save()
