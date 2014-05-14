# -*- coding: utf-8 -*-
"""tests for entity models
"""
import unittest

from ensure import ensure


class ModelTests(unittest.TestCase):
    def test_it_should_have_fields(self):
        from nonobvious import models

        class MyModel(models.Model):
            pass

        ensure(MyModel).has_attribute('fields')

    def test_it_should_populate_fields(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.Field()

        ensure(MyModel.fields).has_key('foo')
        ensure(MyModel.fields['foo']).equals(MyModel.foo)

    def test_it_should_be_immutable(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.Field()

        model = MyModel(foo='bar')
        ensure(model.__setitem__).called_with('foo', 'baz').raises(MyModel.ConstraintError)
        ensure(setattr).called_with(model, 'foo', 'baz').raises(MyModel.ConstraintError)
        ensure(model.__setitem__).called_with('flugle', 'baz').raises(MyModel.ConstraintError)

    def test_it_should_have_a_validation_spec(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.String(required=True)
            bar = fields.Integer(default=2)

        ensure(MyModel.validation_spec).equals(
            {
                '+foo': 'string',
                'bar': 'integer',
            }
        )

    def test_it_should_validate(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.String(required=True)
            bar = fields.Integer(default=2)

        ensure(MyModel).called_with().raises(MyModel.ValidationError)
        ensure(MyModel).called_with(foo='baz').equals({'foo': 'baz', 'bar': 2})
