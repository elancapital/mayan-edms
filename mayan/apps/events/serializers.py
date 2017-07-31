from __future__ import unicode_literals

from django.utils.six import string_types

from actstream.models import Action
from rest_framework import serializers

from common.serializers import ContentTypeSerializer
from rest_api.fields import DynamicSerializerField

from .classes import EventType
from .models import StoredEventType


class EventTypeSerializer(serializers.Serializer):
    label = serializers.CharField()
    name = serializers.CharField()

    def to_representation(self, instance):
        if isinstance(instance, EventType):
            return super(EventTypeSerializer, self).to_representation(
                instance
            )
        elif isinstance(instance, StoredEventType):
            return super(EventTypeSerializer, self).to_representation(
                instance.get_class()
            )
        elif isinstance(instance, string_types):
            return super(EventTypeSerializer, self).to_representation(
                EventType.get(name=instance)
            )


class EventSerializer(serializers.ModelSerializer):
    actor = DynamicSerializerField(read_only=True)
    target = DynamicSerializerField(read_only=True)
    actor_content_type = ContentTypeSerializer(read_only=True)
    target_content_type = ContentTypeSerializer(read_only=True)
    verb = EventTypeSerializer(read_only=True)

    class Meta:
        exclude = (
            'action_object_content_type', 'action_object_object_id'
        )
        model = Action
