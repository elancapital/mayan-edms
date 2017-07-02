from __future__ import unicode_literals

from django.utils import six

__ALL__ = ('MailingBackendMetaclass', 'MailingBackendBase', 'MailingBackend')


class MailingBackendMetaclass(type):
    _registry = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super(MailingBackendMetaclass, mcs).__new__(mcs, name, bases, attrs)
        if not new_class.__module__=='mailer.backends.base':
            mcs._registry['{}.{}'.format(new_class.__module__, name)] = new_class

        return new_class

    @classmethod
    def get(mcs, name):
        return mcs._registry[name]


class MailingBackendBase(object):
    """
    Base class for the mailing backends. This class is mainly a wrapper
    for other Django backends that adds a few metadata to specify the
    fields it needs to be instanciated at runtime.

    The fields attribute is a list of dictionaries with the format:
    {
        'name': ''  # Field internal name
        'label': ''  # Label to show to users
        'class': ''  # Field class to use. Field classes are Python dot
                       paths to Django's form fields.
        'initial': ''  # Field initial value
        'default': ''  # Default value.
    }

    """
    class_path = ''  # Dot path to the actual class that will handle the mail
    fields = ()


class MailingBackend(six.with_metaclass(MailingBackendMetaclass, MailingBackendBase)):
    @classmethod
    def get(cls, name):
        return cls._registry[name]
