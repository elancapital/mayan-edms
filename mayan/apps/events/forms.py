from __future__ import unicode_literals

from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _


class EventTypeUserRelationshipForm(forms.Form):
    namespace = forms.CharField(
        label=_('Namespace'), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    label = forms.CharField(
        label=_('Label'), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    relationship = forms.ChoiceField(
        label=_('Subscription'),
        widget=forms.RadioSelect(), choices=(
            ('none', _('No')),
            ('subscribed', _('Subscribed')),
        )
    )

    def __init__(self, *args, **kwargs):
        super(EventTypeUserRelationshipForm, self).__init__(
            *args, **kwargs
        )

        self.fields['namespace'].initial = self.initial['stored_event_type'].namespace
        self.fields['label'].initial = self.initial['stored_event_type'].label

        relationship = self.initial['stored_event_type'].event_subscriptions.filter(
            user=self.initial['user']
        )
        if relationship.exists():
            self.fields['relationship'].initial = 'subscribed'
        else:
            self.fields['relationship'].initial = 'none'

    def save(self):
        relationship = self.initial['stored_event_type'].event_subscriptions.filter(
            user=self.initial['user']
        )

        if self.cleaned_data['relationship'] == 'none':
            relationship.delete()
        elif self.cleaned_data['relationship'] == 'subscribed':
            if not relationship.exists():
                relationship.create(
                    stored_event_type=self.initial['stored_event_type'],
                    user=self.initial['user']
                )


EventTypeUserRelationshipFormSet = formset_factory(
    EventTypeUserRelationshipForm, extra=0
)
