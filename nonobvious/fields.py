# -*- coding: utf-8 -*-
"""entities.fields
"""
from concon import frozenlist
from concon import ConstraintError
import valideer as V

__all__ = ['Field', 'Integer', 'String']


class NIL: pass


class Field(object):
    @staticmethod
    def validator(v):
        """Validate the field value. By default, anything goes!

        Provide your own validator when subclassing. Can be string or method.
        """
        return True

    choices = None

    def add_validator(self, validator):
        if validator is not None:
            if self.validator is Field.validator:
                self.validator = validator
            else:
                self.validator = V.AllOf(self.validator, validator)

    def __init__(self, key=None, required=False, default=NIL, validator=None, choices=None):
        super(Field, self).__init__()
        self.key = key
        self.required = required
        self.default = default
        self.add_validator(validator)
        if choices is not None:
            self.choices = tuple(choices)
            self.add_validator(V.Enum(self.choices))

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.get(self.key, self.default)

    def __set__(self, obj, value):
        raise ConstraintError("Entity fields are read-only.")

    @property
    def validation_spec(self):
        key = self.key
        if self.required:
            key = '+' + key
        return (key, self.validator)


class Boolean(Field):
    validator = 'boolean'


class Embedded(Field):
    @property
    def validator(self):
        return V.AdaptTo(self.entity)

    @property
    def entity(self):
        if not hasattr(self, '_entity'):
            entity_spec = self.entity_spec
            if isinstance(entity_spec, basestring):
                from . import entities
                self._entity = entities.Entity.entities[entity_spec]
            else:
                self._entity = entity_spec
        return self._entity

    def __init__(self, **kwargs):
        try:
            entity_spec = kwargs.pop('entity')
        except KeyError:
            raise TypeError('Embedded field requires an `entity` argument.')
        super(Embedded, self).__init__(**kwargs)
        self.entity_spec = entity_spec


class String(Field):
    validator = 'string'


class StringList(Field):
    validator = V.AllOf(
        V.HomogeneousSequence(item_schema = 'string'),
        V.AdaptTo(frozenlist)
    )


class Integer(Field):
    validator = 'integer'


class IntegerList(Field):
    validator = V.AllOf(
        V.HomogeneousSequence(item_schema = 'integer'),
        V.AdaptTo(frozenlist)
    )


class Date(Field):
    validator = 'date'


class TimeZoneAwareField(Field):
    @staticmethod
    def has_tzinfo(d):
        return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None

    def __init__(self, **kwargs):
        naive_ok = kwargs.pop('naive_ok', False)
        super(TimeZoneAwareField, self).__init__(**kwargs)
        if not naive_ok:
            self.add_validator(self.has_tzinfo)


class Time(TimeZoneAwareField):
    validator = 'time'


class DateTime(TimeZoneAwareField):
    validator = 'datetime'
