from __future__ import unicode_literals

from document_indexing.tasks import task_index_document


def handler_index_document(sender, **kwargs):
    task_index_document.apply_async(
        document_id=kwargs['instance'].workflow_instance.document.pk
    )
