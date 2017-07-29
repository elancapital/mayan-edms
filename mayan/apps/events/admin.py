from __future__ import unicode_literals

from django.contrib import admin

from .models import EventSubscription, EventType, Notification


@admin.register(EventSubscription)
class EventSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type')


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('name', '__str__')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'read')
