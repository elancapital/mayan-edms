from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from actstream.models import Action

from .classes import Event


@python_2_unicode_compatible
class EventType(models.Model):
    name = models.CharField(
        max_length=64, unique=True, verbose_name=_('Name')
    )

    class Meta:
        verbose_name = _('Event type')
        verbose_name_plural = _('Event types')

    def __str__(self):
        return force_text(self.get_class())

    def get_class(self):
        return Event.get(name=self.name)


@python_2_unicode_compatible
class EventSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_index=True, on_delete=models.CASCADE,
        related_name='event_subscriptions', verbose_name=_('User')
    )
    event_type = models.ForeignKey(
        EventType, on_delete=models.CASCADE,
        related_name='event_subscriptions', verbose_name=_('Event type')
    )

    class Meta:
        verbose_name = _('Event subscription')
        verbose_name_plural = _('Event subscriptions')

    def __str__(self):
        return force_text(self.event_type)


@python_2_unicode_compatible
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_index=True, on_delete=models.CASCADE,
        related_name='notifications', verbose_name=_('User')
    )
    action = models.ForeignKey(
        Action, on_delete=models.CASCADE, related_name='notifications',
        verbose_name=_('Action')
    )
    read = models.BooleanField(default=False, verbose_name=_('Read'))

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        return force_text(self.action)
