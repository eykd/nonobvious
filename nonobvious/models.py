# -*- coding: utf-8 -*-
"""entities.models
"""
from concon import frozendict, ConstraintError
from valideer import ValidationError
import valideer

from . import fields

__all__ = ['Model', 'ConstraintError', 'ValidationError']


class ModelMeta(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'fields'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.fields = {}
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            pass

    def __new__(cls, name, bases, attrs):
        _new = attrs.pop('__new__', None)
        new_attrs = {'__new__': _new} if _new is not None else {}
        new_class = super(ModelMeta, cls).__new__(cls, name, bases, new_attrs)

        validation_spec = []
        for name, value in attrs.items():
            if isinstance(value, fields.Field):
                value.key = name
                new_class.fields[name] = value
                validation_spec.append(value.validation_spec)
            setattr(new_class, name, value)
        new_class.validation_spec = frozendict(validation_spec)
        return new_class


class Model(frozendict):
    """A Model is simply a read-only dict with a light dusting of magic.

    The Model can be subclassed to add fields from ``nonobvious.fields``
    (similar to Django models).

    Model instances provide copy-on-write functionality via the `copy` method.

    """
    __metaclass__ = ModelMeta
    ConstraintError = ConstraintError
    ValidationError = ValidationError

    def __init__(self, *args, **kwargs):
        defaults = {}
        for name, field in self.fields.iteritems():
            if name not in kwargs and field.default is not None:
                defaults[name] = field.default
        for arg in args:
            defaults.update(arg)
        super(Model, self).__init__(defaults, **kwargs)
        validator = valideer.parse(self.validation_spec)
        validator.validate(self)

    def copy(self, *args, **kwargs):
        """Return a shallow copy, optionally with updated members as specified.

        Updated members must pass validation.
        """
        return self.__class__(self, *args, **kwargs)
