# -*- coding: utf-8 -*-
"""entities.fields
"""
from concon import ConstraintError

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
            self.validator = validator

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


class Time(Field):
    validator = 'time'


class DateTime(Field):
    validator = 'datetime'
