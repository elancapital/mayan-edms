from __future__ import unicode_literals

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from actstream import action

from .permissions import permission_events_view


@python_2_unicode_compatible
class Event(object):
    _registry = {}

    @classmethod
    def all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, name):
        try:
            return cls._registry[name]
        except KeyError:
            raise KeyError(
                _('Unknown or obsolete event type: {0}'.format(name))
            )

    def __init__(self, name, label):
        self.name = name
        self.label = label
        self.event_type = None
        self.__class__._registry[name] = self

    def __str__(self):
        return force_text(self.label)

    def get_type(self):
        if not self.event_type:
            EventType = apps.get_model('events', 'EventType')

            self.event_type, created = EventType.objects.get_or_create(
                name=self.name
            )

        return self.event_type

    def commit(self, actor=None, action_object=None, target=None):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )
        Action = apps.get_model(
            app_label='actstream', model_name='Action'
        )
        Notification = apps.get_model(
            app_label='events', model_name='Notification'
        )

        if not self.event_type:
            EventType = apps.get_model('events', 'EventType')
            self.event_type, created = EventType.objects.get_or_create(
                name=self.name
            )

        results = action.send(
            actor or target, actor=actor, verb=self.name,
            action_object=action_object, target=target
        )

        for handler, result in results:
            if isinstance(result, Action):
                for user in get_user_model().objects.all():
                    if user.event_subscriptions.filter(event_type__name=result.verb).exists():
                        if result.target:
                            try:
                                AccessControlList.objects.check_access(
                                    permissions=permission_events_view,
                                    user=user, obj=result.target
                                )
                            except PermissionDenied:
                                pass
                            else:
                                Notification.objects.create(action=result, user=user)
                        else:
                            Notification.objects.create(action=result, user=user)
