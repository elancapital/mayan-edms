from __future__ import absolute_import, unicode_literals

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.template import Context, Template
from django.utils.module_loading import import_string
from django.utils.html import strip_tags
from django.utils.translation import ungettext, ugettext_lazy as _

from common.generics import (
    DynamicFormView, MultipleObjectFormActionView,
    SingleObjectDynamicFormCreateView, SingleObjectListView
)
from documents.models import Document

from .backends import MailingBackend
from .forms import DocumentMailForm, UserMailerDynamicForm
from .models import LogEntry, UserMailer
from .permissions import (
    permission_mailing_link, permission_mailing_send_document,
    permission_view_error_log
)
from .tasks import task_send_document


class LogEntryListView(SingleObjectListView):
    extra_context = {
        'hide_object': True,
        'title': _('Document mailing error log'),
    }
    model = LogEntry
    view_permission = permission_view_error_log


class MailDocumentView(MultipleObjectFormActionView):
    as_attachment = True
    form_class = DocumentMailForm
    model = Document
    object_permission = permission_mailing_send_document

    success_message = _('%(count)d document queued for email delivery')
    success_message_plural = _(
        '%(count)d documents queued for email delivery'
    )
    title = 'Email document'
    title_plural = 'Email documents'
    title_document = 'Email document: %s'

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'submit_icon': 'fa fa-envelope',
            'submit_label': _('Send'),
            'title': ungettext(
                self.title,
                self.title_plural,
                queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _(self.title_document) % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        return {
            'as_attachment': self.as_attachment
        }

    def object_action(self, form, instance):
        context = Context({
            'link': 'http://%s%s' % (
                Site.objects.get_current().domain,
                instance.get_absolute_url()
            ),
            'document': instance
        })
        body_template = Template(form.cleaned_data['body'])
        body_html_content = body_template.render(context)
        body_text_content = strip_tags(body_html_content)

        subject_template = Template(form.cleaned_data['subject'])
        subject_text = strip_tags(subject_template.render(context))

        task_send_document.apply_async(
            args=(
                subject_text, body_text_content, self.request.user.email,
                form.cleaned_data['email']
            ), kwargs={
                'document_id': instance.pk,
                'as_attachment': self.as_attachment
            }
        )


class MailDocumentLinkView(MailDocumentView):
    as_attachment = False
    object_permission = permission_mailing_link
    success_message = _('%(count)d document link queued for email delivery')
    success_message_plural = _(
        '%(count)d document links queued for email delivery'
    )
    title = 'Email document link'
    title_plural = 'Email document links'
    title_document = 'Email link for document: %s'


class UserMailingCreateView(SingleObjectDynamicFormCreateView):
    form_class = UserMailerDynamicForm

    #view_permission = permission_folder_create
    #TODO: create mailer permissions

    #TODO: fix post action
    post_action_redirect = reverse_lazy('mailer:user_mailer_list')

    def get_backend(self):
        try:
            return MailingBackend.get(name=self.kwargs['class_path'])
        except KeyError:
            raise Http404(
                '{} class not found'.format(self.kwargs['class_path'])
            )

    def get_extra_context(self):
        return {
            'title': _('Create a "%s" mailer') % self.get_backend().label,
        }

    def get_form_schema(self):
        return {'fields': self.get_backend().fields}

    def get_instance_extra_data(self):
        return {'backend_path': self.kwargs['class_path']}


class UserMailerListView(SingleObjectListView):
    extra_context = {
        'hide_object': True,
        'title': _('User mailers'),
    }
    model = UserMailer
    #view_permission = permission_view_error_log
    #TODO: add permission_user_mailer_view
