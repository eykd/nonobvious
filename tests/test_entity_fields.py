# -*- coding: utf-8 -*-
"""test for entity fields
"""
import datetime as dt
import unittest

from ensure import ensure

import valideer as V


class FieldTests(unittest.TestCase):
    def test_it_should_be_a_descriptor(self):
        from nonobvious import fields

        class MyModel(dict):
            foo = fields.Field(key='foo')

        model = MyModel(foo="bar")
        ensure(model.foo).equals("bar")

    def test_it_should_have_defaults(self):
        from nonobvious import fields

        class MyModel(dict):
            foo = fields.Field(default='bar')

        model = MyModel()
        ensure(model.foo).equals("bar")

    def test_it_should_have_a_validation_spec(self):
        from nonobvious import fields
        field = fields.Field(key='foo', validator='string')
        ensure(field.validation_spec).equals(('foo', 'string'))

    def test_it_should_have_a_required_validation_spec(self):
        from nonobvious import fields
        field = fields.Field(key='foo', validator='string', required=True)
        ensure(field.validation_spec).equals(('+foo', 'string'))

    def test_it_should_accept_and_enforce_choices(self):
        from nonobvious import fields

        field = fields.Field(key='foo', validator='string', choices=('bar', 'baz'))

        validator = V.parse(dict([field.validation_spec]))

        ensure(validator.validate).called_with({'foo': 'bar'}).equals({'foo': 'bar'})
        ensure(validator.validate).called_with({'foo': 'baz'}).equals({'foo': 'baz'})
        ensure(validator.validate).called_with({'foo': 'boo'}).raises(V.ValidationError)


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
        field = fields.Time(key='foo', naive_ok=True)
        ensure(field.validation_spec).equals(('foo', 'time'))

    def test_it_should_not_accept_naive_times(self):
        from nonobvious import fields

        field = fields.Time(key='foo')

        ensure(
            V.parse(dict([field.validation_spec])).validate
        ).called_with(
            {'foo': dt.datetime.now().time()}  # Naive time
        ).raises(
            V.ValidationError
        )

    def test_it_should_accept_timezone_aware_times(self):
        from nonobvious import fields
        from pytz import timezone

        field = fields.Time(key='foo')
        tz_now = timezone('UTC').localize(dt.datetime.now().time())

        ensure(
            V.parse(dict([field.validation_spec])).validate
        ).called_with(
            {'foo': tz_now}
        ).equals(
            {'foo': tz_now}
        )

    def test_it_should_accept_timezone_aware_times_even_with_custom_validator(self):
        from nonobvious import fields
        from pytz import timezone
        UTC = timezone('UTC')

        field = fields.Time(key='foo', validator=lambda d: d > UTC.localize(dt.time(1, 1, 1)))
        tz_now = UTC.localize(dt.datetime.now().time())

        ensure(
            V.parse(dict([field.validation_spec])).validate
        ).called_with(
            {'foo': tz_now}
        ).equals(
            {'foo': tz_now}
        )


class DateTimeFieldTests(unittest.TestCase):
    def test_it_should_have_validation_spec(self):
        from nonobvious import fields
        field = fields.DateTime(key='foo', naive_ok=True)
        ensure(field.validation_spec).equals(('foo', 'datetime'))

    def test_it_should_not_accept_naive_datetimes(self):
        from nonobvious import fields

        field = fields.DateTime(key='foo')

        ensure(
            V.parse(dict([field.validation_spec])).validate
        ).called_with(
            {'foo': dt.datetime.now()}  # Naive datetime
        ).raises(
            V.ValidationError
        )

    def test_it_should_accept_timezone_aware_datetimes(self):
        from nonobvious import fields
        from pytz import timezone

        field = fields.DateTime(key='foo')
        tz_now = timezone('UTC').localize(dt.datetime.now())

        ensure(
            V.parse(dict([field.validation_spec])).validate
        ).called_with(
            {'foo': tz_now}
        ).equals(
            {'foo': tz_now}
        )

    def test_it_should_accept_timezone_aware_datetimes_even_with_custom_validator(self):
        from nonobvious import fields
        from pytz import timezone
        UTC = timezone('UTC')

        field = fields.DateTime(key='foo', validator=lambda d: d > UTC.localize(dt.datetime(1, 1, 1)))
        tz_now = UTC.localize(dt.datetime.now())

        ensure(
            V.parse(dict([field.validation_spec])).validate
        ).called_with(
            {'foo': tz_now}
        ).equals(
            {'foo': tz_now}
        )
