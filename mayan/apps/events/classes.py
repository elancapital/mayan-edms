from __future__ import unicode_literals

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils.encoding import force_text, python_2_unicode_compatible

from actstream import action

from .permissions import permission_events_view

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class EventTypeNamespace(object):
    _registry = {}

    @classmethod
    def all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, name, label):
        self.name = name
        self.label = label
        self.event_types = []
        self.__class__._registry[name] = self

    def __str__(self):
        return force_text(self.label)

    def add_event_type(self, name, label):
        event_type = EventType(namespace=self, name=name, label=label)
        self.event_types.append(event_type)
        return event_type


@python_2_unicode_compatible
class EventType(object):
    _registry = {}

    @classmethod
    def all(cls):
        # Return sorted permisions by namespace.name
        return sorted(
            cls._registry.values(), key=lambda x: x.namespace.name
        )

    @classmethod
    def get(cls, name):
        try:
            return cls._registry[name]
        except KeyError:
            raise KeyError(
                'Unknown or obsolete event type: {0}'.format(name)
            )

    def __init__(self, namespace, name, label):
        self.namespace = namespace
        self.name = name
        self.label = label
        self.stored_event_type = None
        self.__class__._registry[self.id] = self

    def __str__(self):
        return force_text('{}: {}'.format(self.namespace.label, self.label))

    @property
    def id(self):
        return '%s.%s' % (self.namespace.name, self.name)

    @classmethod
    def refresh(cls):
        for event_type in cls.all():
            event_type.get_stored_event_type()

    def get_stored_event_type(self):
        if not self.stored_event_type:
            StoredEventType = apps.get_model('events', 'StoredEventType')

            self.stored_event_type, created = StoredEventType.objects.get_or_create(
                name=self.id
            )

        return self.stored_event_type

    def commit(self, actor=None, action_object=None, target=None):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )
        Action = apps.get_model(
            app_label='actstream', model_name='Action'
        )
        ContentType = apps.get_model(
            app_label='contenttypes', model_name='ContentType'
        )
        Notification = apps.get_model(
            app_label='events', model_name='Notification'
        )

        results = action.send(
            actor or target, actor=actor, verb=self.id,
            action_object=action_object, target=target
        )

        for handler, result in results:
            if isinstance(result, Action):
                for user in get_user_model().objects.all():
                    if user.event_subscriptions.filter(stored_event_type__name=result.verb).exists():
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

                    if result.target:
                        content_type = ContentType.objects.get_for_model(model=result.target)

                        relationship = user.object_subscriptions.filter(
                            content_type=content_type,
                            object_id=result.target.pk,
                            stored_event_type__name=result.verb
                        )

                        if relationship.exists():
                            try:
                                AccessControlList.objects.check_access(
                                    permissions=permission_events_view,
                                    user=user, obj=result.target
                                )
                            except PermissionDenied:
                                pass
                            else:
                                Notification.objects.create(action=result, user=user)
