from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from permissions import PermissionNamespace

namespace = PermissionNamespace('task_manager', _('Task manager'))

permission_task_view = namespace.add_permission(
    name='task_view', label=_('View tasks')
)
#permission_mailing_send_document = namespace.add_permission(
#    name='mail_document', label=_('Send document via email')
#)
#permission_view_error_log = namespace.add_permission(
#    name='view_error_log', label=_('View document mailing error log')
#)
