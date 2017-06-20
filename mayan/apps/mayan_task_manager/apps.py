from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from common import MayanAppConfig, menu_object, menu_multi_item, menu_tools
from common.widgets import two_state_template
from navigation import SourceColumn

from .classes import CeleryQueue, Task, TaskType
from .links import (
    link_queue_list, link_queue_active_task_list,
    link_queue_scheduled_task_list, link_queue_reserved_task_list
)


class TaskManagerApp(MayanAppConfig):
    app_namespace = 'task_manager'
    app_url = 'task_manager'
    name = 'mayan_task_manager'
    verbose_name = _('Task manager')

    def ready(self):
        super(TaskManagerApp, self).ready()

        SourceColumn(
            source=CeleryQueue, label=_('Label'), attribute='label'
        )
        SourceColumn(
            source=CeleryQueue, label=_('Default queue?'),
            func=lambda context: two_state_template(
                context['object'].is_default_queue
            )
        )
        SourceColumn(
            source=Task, label=_('Type'), attribute='task_type'
        )
        SourceColumn(
            source=Task, label=_('Start time'), attribute='get_time_started'
        )
        SourceColumn(
            source=Task, label=_('Host'),
            func=lambda context: context['object'].kwargs['hostname']
        )
        SourceColumn(
            source=Task, label=_('Acknowledged'),
            func=lambda context: two_state_template(
                context['object'].kwargs['acknowledged']
            )
        )
        SourceColumn(
            source=Task, label=_('Arguments'),
            func=lambda context: context['object'].kwargs['args']
        )
        SourceColumn(
            source=Task, label=_('Keyword arguments'),
            func=lambda context: context['object'].kwargs['kwargs']
        )
        SourceColumn(
            source=Task, label=_('Worker process ID'),
            func=lambda context: context['object'].kwargs['worker_pid']
        )

        menu_object.bind_links(
            links=(
                link_queue_active_task_list, link_queue_scheduled_task_list,
                link_queue_reserved_task_list,
            ), sources=(CeleryQueue,)
        )

        menu_tools.bind_links(links=(link_queue_list,))

        ## TEMP
        TaskType(name='ocr.tasks.task_do_ocr', label=_('Document version OCR'))
