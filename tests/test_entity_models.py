# -*- coding: utf-8 -*-
"""tests for entity models
"""
import unittest

from ensure import ensure


class ModelTests(unittest.TestCase):
    def test_base_model_should_not_have_fields(self):
        from nonobvious import models

        ensure(getattr).called_with(models.Model, 'fields').raises(AttributeError)

    def test_it_should_have_fields(self):
        from nonobvious import models

        class MyModel(models.Model):
            pass

        ensure(MyModel).has_attribute('fields')

    def test_multiple_models_should_not_share_fields(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.Field()

        class MyOtherModel(models.Model):
            bar = fields.Field()

        ensure(MyModel.fields).has_length(1)
        ensure(MyOtherModel.fields).has_length(1)

    def test_it_should_populate_fields(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.Field()

        ensure(MyModel.fields).has_key('foo')
        ensure(MyModel.fields['foo']).equals(MyModel.foo)

    def test_it_should_populate_defaults(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.Field(default='bar')

        model = MyModel()
        ensure(model.foo).equals("bar")
        ensure(model['foo']).equals("bar")

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
        ensure(MyModel).called_with(blah='!!!').raises(MyModel.ValidationError)
        ensure(MyModel).called_with(foo='baz').equals({'foo': 'baz', 'bar': 2})

    def test_it_should_produce_a_copy(self):
        from nonobvious import models
        from nonobvious import fields

        class MyModel(models.Model):
            foo = fields.String(required=True)
            bar = fields.Integer(default=2)

        model1 = MyModel(foo='baz')
        model2 = model1.copy()
        ensure(model2).is_not(model1)
        ensure(model2).equals(model1)

        model3 = model2.copy(bar=3)
        ensure(model3).does_not_equal(model2)
        ensure(model3['foo']).equals(model2['foo'])
        ensure(model3['bar']).equals(3)
