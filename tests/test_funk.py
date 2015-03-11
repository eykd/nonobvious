# -*- coding: utf-8 -*-
"""Tests for nonobvious.events
"""
import sys
import unittest

import operator as op
import functools

from ensure import ensure
from mock import Mock, patch
from nose.plugins.attrib import attr

from nonobvious import funk


class FunkTests(unittest.TestCase):
    def setUp(self):
        def f(*args):
            return args

        self.f = f

        def double(x):
            return x * 2

        self.double = double

    def test_debugger_should_start_ipdb_debugger(self):
        ipdb_set_trace = Mock()
        with patch('ipdb.set_trace', ipdb_set_trace):
            funk.debugger()
            ipdb_set_trace.assert_called_once_with()

    def test_debugger_should_start_pdb_debugger(self):
        pdb_set_trace = Mock()

        orig_import = __import__

        def dont_import_ipdb(mod, *args):
            if mod == 'ipdb':
                raise ImportError
            else:
                return orig_import(mod, *args)

        with patch('pdb.set_trace', pdb_set_trace):
            with patch('__builtin__.__import__', side_effect=dont_import_ipdb):
                funk.debugger()
                pdb_set_trace.assert_called_once_with()

    def test_get_positional_arg_count_counts_positional_arguments(self):
        def foo(a, b): pass

        ensure(funk.get_positional_arg_count).called_with(foo).equals(2)

        def bar(a, b, c=None): pass

        ensure(funk.get_positional_arg_count).called_with(bar).equals(2)

        def baz(a, b, c, d, e=None): pass

        ensure(funk.get_positional_arg_count).called_with(baz).equals(4)

        def boo(*args): pass

        ensure(funk.get_positional_arg_count).called_with(boo).equals(0)

        # C functions can't be inspected:
        ensure(funk.get_positional_arg_count).called_with(op.add).equals(None)

    def test_reverse_args_should_reverse_args_arguments(self):
        reversed_args = funk.reverse_args(self.f)

        ensure(reversed_args).called_with(1, 2, 3).equals((3, 2, 1))

    def test_partial_should_create_a_partially_applied_function(self):
        curried = funk.partial(self.f)
        ensure(curried).called_with(1, 2, 3).equals((1, 2, 3))

        curried = funk.partial(self.f, 1)
        ensure(curried).called_with(2, 3).equals((1, 2, 3))

    def test_compose_should_create_nested_functional_calls(self):
        fc = funk.compose(str, funk.curry(op.add)(2))
        ensure(fc).called_with(2).equals('4')

    def test_pipeline_should_create_functional_pipelines(self):
        fc = funk.pipeline(str, funk.curry(op.add)('2'))
        ensure(fc).called_with(2).equals('22')

    def test_curry_should_create_a_self_partialing_function(self):
        curried = funk.curry(self.f)
        curried1 = curried(1, 2, 3)
        ensure(curried1).called_with().equals((1, 2, 3))
        curried2 = curried(1, 2)
        ensure(curried2).called_with(3).equals((1, 2, 3))
        curried3 = curried(1)
        ensure(curried3).called_with(2, 3).equals((1, 2, 3))

    def test_curried_function_should_execute_if_all_args_are_provided(self):
        def f(a, b, c):
            return (a, b, c)

        cf = funk.curry(f)

        cf(1, 2, 3)

        ensure(cf).called_with(1).is_a(functools.partial)
        ensure(cf).called_with(1, 2, 3).equals((1, 2, 3))

    def test_doc_should_overwrite_a_functions_documentation(self):
        new_docs = "The new docs!"
        funk.doc(new_docs, self.f)
        ensure(self.f.__doc__).equals(new_docs)

    def test_fluent_method_should_always_return_self(self):
        class Foo(object):
            def __init__(self):
                self.stuff = []

            @funk.fluent
            def bar(self, blah):
                self.stuff.append(blah)

        foo = Foo()

        ensure(foo.bar).called_with(5).is_(foo)
        ensure(foo.stuff).has_length(1)
        ensure(foo.stuff).contains(5)

    def test_get_attr_should_work_like_getattr_but_with_keywords(self):
        class Foo(object): pass
        ensure(funk.get_attr).called_with('__name__', Foo).equals('Foo')
        ensure(funk.get_attr).called_with('bar', None, 5).equals(5)
        ensure(funk.get_attr).called_with('bar', None, default=5).equals(5)

    def test_get_attr_from_should_work_like_getattr_but_with_keywords(self):
        class Foo(object): pass
        ensure(funk.get_attr_from).called_with(Foo, '__name__').equals('Foo')
        ensure(funk.get_attr_from).called_with(None, 'bar', 5).equals(5)
        ensure(funk.get_attr_from).called_with(None, 'bar', default=5).equals(5)

    def test_getitem_should_work_like_dict_get(self):
        foo = {'foo': 'bar'}
        ensure(funk.get_item).called_with('foo', foo).equals('bar')
        ensure(funk.get_item).called_with('blah', foo, 5).equals(5)
        ensure(funk.get_item).called_with('blah', foo, default=5).equals(5)

    def test_set_item_on_should_update_a_deep_copy(self):
        foo = {'foo': {'bar': 'baz'}}
        ensure(funk.set_item_on).called_with(foo, 'blah', 5).equals({'foo': {'bar': 'baz'}, 'blah': 5})
        ensure(funk.set_item_on).called_with(foo, 'blah', 5).is_not(foo)
        ensure(funk.set_item_on(foo, 'blah', 5)['foo']).is_not(foo['foo'])

    def test_set_item_should_update_a_deep_copy(self):
        foo = {'foo': {'bar': 'baz'}}
        ensure(funk.set_item).called_with('blah', 5, foo).equals({'foo': {'bar': 'baz'}, 'blah': 5})
        ensure(funk.set_item).called_with('blah', 5, foo).is_not(foo)
        ensure(funk.set_item('blah', 5, foo)['foo']).is_not(foo['foo'])

    def test_set_slice_on_should_update_a_deep_copy(self):
        foo = ['foo', 'bar', 'baz', ['falala']]
        ensure(funk.set_slice_on).called_with(foo, slice(1, 2), ['blah']).equals(['foo', 'blah', 'baz', ['falala']])
        ensure(funk.set_slice_on).called_with(foo, slice(1, 2), ['blah']).is_not(foo)
        ensure(funk.set_slice_on(foo, slice(1, 2), ['blah'])[-1]).is_not(foo[-1])

    def test_set_slice_should_update_a_deep_copy(self):
        foo = ['foo', 'bar', 'baz', ['falala']]
        ensure(funk.set_slice).called_with(slice(1, 2), ['blah'], foo).equals(['foo', 'blah', 'baz', ['falala']])
        ensure(funk.set_slice).called_with(slice(1, 2), ['blah'], foo).is_not(foo)
        ensure(funk.set_slice(slice(1, 2), ['blah'], foo)[-1]).is_not(foo[-1])

    def test_delete_item_on_should_update_a_deep_copy(self):
        foo = {'foo': {'bar': 'baz'}, 'blah': 5}
        ensure(funk.delete_item_on).called_with(foo, 'blah').equals({'foo': {'bar': 'baz'}})
        ensure(funk.delete_item_on).called_with(foo, 'blah').is_not(foo)
        ensure(funk.delete_item_on(foo, 'blah')['foo']).is_not(foo['foo'])

    def test_delete_item_should_update_a_deep_copy(self):
        foo = {'foo': {'bar': 'baz'}, 'blah': 5}
        ensure(funk.delete_item).called_with('blah', foo).equals({'foo': {'bar': 'baz'}})
        ensure(funk.delete_item).called_with('blah', foo).is_not(foo)
        ensure(funk.delete_item('blah', foo)['foo']).is_not(foo['foo'])

    def test_delete_slice_on_should_update_a_deep_copy(self):
        foo = ['foo', 'blah', 'bar', 'baz', ['falala']]
        ensure(funk.delete_slice_on).called_with(foo, slice(1, 2)).equals(['foo', 'bar', 'baz', ['falala']])
        ensure(funk.delete_slice_on).called_with(foo, slice(1, 2)).is_not(foo)
        ensure(funk.delete_slice_on(foo, slice(1, 2))[-1]).is_not(foo[-1])

    def test_delete_slice_should_update_a_deep_copy(self):
        foo = ['foo', 'blah', 'bar', 'baz', ['falala']]
        ensure(funk.delete_slice).called_with(slice(1, 2), foo).equals(['foo', 'bar', 'baz', ['falala']])
        ensure(funk.delete_slice).called_with(slice(1, 2), foo).is_not(foo)
        ensure(funk.delete_slice(slice(1, 2), foo)[-1]).is_not(foo[-1])

    def test_before_should_create_before_decorators(self):
        out = []

        def run_before():
            out.append('Before!')

        @funk.before(run_before)
        def something():
            out.append('Something!')
            return 5

        ensure(something).called_with().equals(5)
        ensure(out).equals(['Before!', 'Something!'])

    def test_after_should_create_after_decorators(self):
        out = []

        def run_after():
            out.append('After!')

        @funk.after(run_after)
        def something():
            out.append('Something!')
            return 5

        ensure(something).called_with().equals(5)
        ensure(out).equals(['Something!', 'After!'])

    def test_around_should_create_around_decorators(self):
        @funk.around
        def maybe(func, value):
            if value is not None:
                return func(value)

        ensure(maybe(self.double)(2)).equals(4)
        ensure(maybe(self.double)(None)).is_none()

    def test_provided_should_guard_a_function(self):
        maybe = funk.provided(lambda x: x is not None)

        ensure(maybe(self.double)(2)).equals(4)
        ensure(maybe(self.double)(None)).is_none()

    def test_map_should_map_a_function_to_a_sequence(self):
        sequence = [1, 2, 3]
        ensure(list(funk.map(self.double, sequence))).equals([2, 4, 6])

    def test_map_on_should_map_a_function_to_a_sequence(self):
        sequence = [1, 2, 3]
        ensure(list(funk.map_on(sequence, self.double))).equals([2, 4, 6])

    def test_reduce_should_reduce_a_sequence_using_a_function(self):
        sequence = [1, 2, 3]
        ensure(funk.reduce).called_with(funk.add, sequence).equals(6)
        ensure(funk.reduce).called_with(funk.add, sequence, 6).equals(12)
        ensure(funk.reduce).called_with(funk.add, sequence, initial=6).equals(12)

    def test_reduce_on_should_reduce_a_sequence_using_a_function(self):
        sequence = [1, 2, 3]
        ensure(funk.reduce_on).called_with(sequence, funk.add).equals(6)
        ensure(funk.reduce_on).called_with(sequence, funk.add, 6).equals(12)
        ensure(funk.reduce_on).called_with(sequence, funk.add, initial=6).equals(12)
