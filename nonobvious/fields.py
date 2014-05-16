# -*- coding: utf-8 -*-
"""entities.fields
"""
from concon import ConstraintError
import valideer as V

__all__ = ['Field', 'Integer', 'String']


class Field(object):
    @staticmethod
    def validator(v):
        """Validate the field value. By default, anything goes!

        Provide your own validator when subclassing. Can be string or method.
        """
        return True

    def __init__(self, key=None, required=False, default=None, validator=None):
        super(Field, self).__init__()
        self.key = key
        self.required = required
        self.default = default
        if validator is not None:
            if self.validator is Field.validator:
                self.validator = validator
            else:
                self.validator = V.AllOf(self.validator, validator)

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


class String(Field):
    validator = 'string'


class Integer(Field):
    validator = 'integer'


class Date(Field):
    validator = 'date'


def _has_tzinfo(d):
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None


def _validate_tz(kwargs):
    naive_ok = kwargs.pop('naive_ok', False)
    if not naive_ok:
        validator = kwargs.get('validator')
        if validator is not None:
            validator = V.AllOf(validator, _has_tzinfo)
        else:
            validator = _has_tzinfo
        kwargs['validator'] = validator
    return kwargs


class Time(Field):
    validator = 'time'

    def __init__(self, **kwargs):
        super(Time, self).__init__(**_validate_tz(kwargs))


class DateTime(Field):
    validator = 'datetime'

    def __init__(self, **kwargs):
        super(DateTime, self).__init__(**_validate_tz(kwargs))
