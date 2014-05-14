# -*- coding: utf-8 -*-
"""test for entity fields
"""
import unittest

from ensure import ensure


class FieldTests(unittest.TestCase):
    def test_it_should_be_a_descriptor(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.Field()

        model = MyModel(foo="bar")
        ensure(model.foo).equals("bar")
        ensure(model['foo']).equals("bar")

    def test_it_should_have_defaults(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.Field(default='bar')

        model = MyModel()
        ensure(model.foo).equals("bar")
        ensure(model['foo']).equals("bar")

    def test_it_should_have_a_validation_spec(self):
        from nonobvious import fields
        field = fields.Field(key='foo', validator='string')
        ensure(field.validation_spec).equals(('foo', 'string'))

    def test_it_should_have_a_required_validation_spec(self):
        from nonobvious import fields
        field = fields.Field(key='foo', validator='string', required=True)
        ensure(field.validation_spec).equals(('+foo', 'string'))


class StringFieldTests(unittest.TestCase):
    def test_it_should_have_validation_spec(self):
        from nonobvious import fields
        field = fields.String(key='foo')
        ensure(field.validation_spec).equals(('foo', 'string'))


class IntegerFieldTests(unittest.TestCase):
    def test_it_should_have_validation_spec(self):
        from nonobvious import fields
        field = fields.Integer(key='foo')
        ensure(field.validation_spec).equals(('foo', 'integer'))


class DateFieldTests(unittest.TestCase):
    def test_it_should_have_validation_spec(self):
        from nonobvious import fields
        field = fields.Date(key='foo')
        ensure(field.validation_spec).equals(('foo', 'date'))


class TimeFieldTests(unittest.TestCase):
    def test_it_should_have_validation_spec(self):
        from nonobvious import fields
        field = fields.Time(key='foo')
        ensure(field.validation_spec).equals(('foo', 'time'))


class DateTimeFieldTests(unittest.TestCase):
    def test_it_should_have_validation_spec(self):
        from nonobvious import fields
        field = fields.DateTime(key='foo')
        ensure(field.validation_spec).equals(('foo', 'datetime'))
