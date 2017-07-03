from __future__ import unicode_literals

import json

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from common.forms import DynamicModelForm

from .classes import MailerBackend
from .models import UserMailer
from .settings import (
    setting_document_body_template, setting_document_subject_template,
    setting_link_body_template, setting_link_subject_template
)


class DocumentMailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        as_attachment = kwargs.pop('as_attachment', False)
        super(DocumentMailForm, self).__init__(*args, **kwargs)
        if as_attachment:
            self.fields[
                'subject'
            ].initial = setting_document_subject_template.value

            self.fields[
                'body'
            ].initial = setting_document_body_template.value % {
                'project_title': settings.PROJECT_TITLE,
                'project_website': settings.PROJECT_WEBSITE
            }
        else:
            self.fields[
                'subject'
            ].initial = setting_link_subject_template.value
            self.fields['body'].initial = setting_link_body_template.value % {
                'project_title': settings.PROJECT_TITLE,
                'project_website': settings.PROJECT_WEBSITE
            }
    email = forms.EmailField(label=_('Email address'))
    subject = forms.CharField(label=_('Subject'), required=False)
    body = forms.CharField(
        label=_('Body'), widget=forms.widgets.Textarea(), required=False
    )


class UserMailerBackendSelectionForm(forms.Form):
    backend = forms.ChoiceField(choices=(), label=_('Backend'))

    def __init__(self, *args, **kwargs):
        super(UserMailerBackendSelectionForm, self).__init__(*args, **kwargs)

        self.fields['backend'].choices=[
            (
                key, backend.label
            ) for key, backend in MailerBackend.get_all().items()
        ]


class UserMailerDynamicForm(DynamicModelForm):
    class Meta:
        fields = ('label', 'default', 'backend_data')
        model = UserMailer
        widgets = {'backend_data': forms.widgets.HiddenInput}

    def __init__(self, *args, **kwargs):
        result = super(UserMailerDynamicForm, self).__init__(*args, **kwargs)
        if self.instance.backend_data:
            for key, value in json.loads(self.instance.backend_data).items():
                self.fields[key].initial = value

        return result

    def clean(self):
        data = super(UserMailerDynamicForm, self).clean()

        # Consolidate the dynamic fields into a single JSON field called
        # 'backend_data'.
        backend_data = {}

        for field in self.schema['fields']:
            backend_data[field['name']] = data.pop(
                field['name'], field.get('default', None)
            )

        data['backend_data'] = json.dumps(backend_data)
        return data
