from __future__ import unicode_literals

from django.db.models.signals import pre_save
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from documents.models import Document, DocumentVersion

from .classes import QuotaBackend
from .exceptions import QuotaExceeded

__all__ = ('DocumentStorageQuota',)


class DocumentStorageQuota(QuotaBackend):
    fields = (
        {
            'name': 'storage_size', 'label': _('Storage size'),
            'class': 'django.forms.FloatField',
            'help_text': _('Total storage usage in megabytes (MB)')
        },
    )
    label = _('Document storage')
    sender = Document
    signal = pre_save

    def __init__(self, storage_size):
        self.storage_size = storage_size

    def _allowed(self):
        return self.storage_size * 1024 * 1024

    def _usage(self, **kwargs):
        total_usage = 0
        for document_version in DocumentVersion.objects.all():
            if document_version.exists():
                total_usage += document_version.file.size

        return total_usage

    def display(self):
        return _(
            'Maximum storage usage: %(formatted_file_size)s (%(raw_file_size)s MB)'
        ) % {
            'formatted_file_size': filesizeformat(self._allowed()),
            'raw_file_size': self.storage_size
        }

    def process(self, **kwargs):
        if self._usage() > self.storage_size * 1024 * 1024:
            raise QuotaExceeded('Storage usage exceeded')

    def usage(self):
        return _('%(usage)s out of %(allowed)s') % {
            'usage': filesizeformat(self._usage()),
            'allowed': filesizeformat(self._allowed())
        }
