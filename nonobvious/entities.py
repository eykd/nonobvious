# -*- coding: utf-8 -*-
"""nonobvious.entities
"""
from concon import frozendict, ConstraintError
from valideer import ValidationError
import valideer

from . import fields

__all__ = ['Entity', 'ConstraintError', 'ValidationError']


class EntityMeta(type):
    def __new__(cls, name, bases, attrs):
        _new = attrs.pop('__new__', None)
        new_attrs = {'__new__': _new} if _new is not None else {}
        new_class = super(EntityMeta, cls).__new__(cls, name, bases, new_attrs)

        if not hasattr(new_class, 'entities'):
            # This branch only executes when processing the base class itself.
            # So, since this is a new base class, not an implementation, this
            # class shouldn't be registered as an implementation. Instead, it sets up a
            # dict where implementations can be registered later.
            new_class.entities = {}
            for name, value in attrs.items():
                setattr(new_class, name, value)
        else:
            # This must be a model implementation, which should be registered.
            # Then it gets its own fields record.
            new_class.entities[name] = new_class
            new_class.fields = {}

            validation_spec = []
            for name, value in attrs.items():
                if isinstance(value, fields.Field):
                    value.key = name
                    new_class.fields[name] = value
                    validation_spec.append(value.validation_spec)
                setattr(new_class, name, value)
            new_class.validation_spec = frozendict(validation_spec)
        return new_class


class Entity(frozendict):
    """A Entity is simply a read-only dict with a light dusting of magic.

    The Entity can be subclassed to add fields from ``nonobvious.fields``
    (similar to Django models).

    Entity instances provide copy-on-write functionality via the `copy` method.

    """
    __metaclass__ = EntityMeta
    ConstraintError = ConstraintError
    ValidationError = ValidationError

    def __init__(self, *args, **kwargs):
        data = {}
        for name, field in self.fields.iteritems():
            if name not in kwargs and field.default is not fields.NIL:
                data[name] = field.default
        for arg in args:
            data.update(arg)
        data.update(kwargs)
        validator = valideer.parse(self.validation_spec)
        super(Entity, self).__init__(validator.validate(data))

    def copy(self, *args, **kwargs):
        """Return a shallow copy, optionally with updated members as specified.

        Updated members must pass validation.
        """
        return self.__class__(self, *args, **kwargs)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, super(Entity, self).__repr__())
