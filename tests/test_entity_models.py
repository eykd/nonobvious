# -*- coding: utf-8 -*-
"""tests for entities
"""
import unittest

from ensure import ensure


class EntityTests(unittest.TestCase):
    def test_base_entity_should_not_have_fields(self):
        from nonobvious import entities

        ensure(getattr).called_with(entities.Entity, 'fields').raises(AttributeError)

    def test_it_should_have_fields(self):
        from nonobvious import entities

        class MyEntity(entities.Entity):
            pass

        ensure(MyEntity).has_attribute('fields')

    def test_multiple_entities_should_not_share_fields(self):
        from nonobvious import entities
        from nonobvious import fields

        class MyEntity(entities.Entity):
            foo = fields.Field()

        class MyOtherEntity(entities.Entity):
            bar = fields.Field()

        ensure(MyEntity.fields).has_length(1)
        ensure(MyOtherEntity.fields).has_length(1)

    def test_it_should_populate_fields(self):
        from nonobvious import entities
        from nonobvious import fields

        class MyEntity(entities.Entity):
            foo = fields.Field()

        ensure(MyEntity.fields).has_key('foo')
        ensure(MyEntity.fields['foo']).equals(MyEntity.foo)

    def test_it_should_populate_defaults(self):
        from nonobvious import entities
        from nonobvious import fields

        class MyEntity(entities.Entity):
            foo = fields.Field(default='bar')

        entity = MyEntity()
        ensure(entity.foo).equals("bar")
        ensure(entity['foo']).equals("bar")

    def test_it_should_be_immutable(self):
        from nonobvious import entities
        from nonobvious import fields

        class MyEntity(entities.Entity):
            foo = fields.Field()

        entity = MyEntity(foo='bar')
        ensure(entity.__setitem__).called_with('foo', 'baz').raises(MyEntity.ConstraintError)
        ensure(setattr).called_with(entity, 'foo', 'baz').raises(MyEntity.ConstraintError)
        ensure(entity.__setitem__).called_with('flugle', 'baz').raises(MyEntity.ConstraintError)

    def test_it_should_have_a_validation_spec(self):
        from nonobvious import entities
        from nonobvious import fields

        class MyEntity(entities.Entity):
            foo = fields.String(required=True)
            bar = fields.Integer(default=2)

        ensure(MyEntity.validation_spec).equals(
            {
                '+foo': 'string',
                'bar': 'integer',
            }
        )

    def test_it_should_validate(self):
        from nonobvious import entities
        from nonobvious import fields

        class MyEntity(entities.Entity):
            foo = fields.String(required=True)
            bar = fields.Integer(default=2)

        ensure(MyEntity).called_with().raises(MyEntity.ValidationError)
        ensure(MyEntity).called_with(blah='!!!').raises(MyEntity.ValidationError)
        ensure(MyEntity).called_with(foo='baz').equals({'foo': 'baz', 'bar': 2})

    def test_it_should_produce_a_copy(self):
        from nonobvious import entities
        from nonobvious import fields

        class MyEntity(entities.Entity):
            foo = fields.String(required=True)
            bar = fields.Integer(default=2)

        entity1 = MyEntity(foo='baz')
        entity2 = entity1.copy()
        ensure(entity2).is_not(entity1)
        ensure(entity2).equals(entity1)

        entity3 = entity2.copy(bar=3)
        ensure(entity3).does_not_equal(entity2)
        ensure(entity3['foo']).equals(entity2['foo'])
        ensure(entity3['bar']).equals(3)

    def test_it_should_represent_itself_as_a_string(self):
        from nonobvious import entities
        from nonobvious import fields

        class MyEntity(entities.Entity):
            foo = fields.String()

        entity = MyEntity(foo='baz')
        ensure(repr(entity)).equals("<MyEntity {'foo': 'baz'}>")

        entity = MyEntity(foo='snickerdoodle')
        ensure(repr(entity)).equals("<MyEntity {'foo': 'snicke...}>")
