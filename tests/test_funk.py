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


def f(*args):
    return args


def double(x):
    return x * 2


class append_to_doc_Tests(unittest.TestCase):
    def test_should_append_to_a_functions_docstring(self):
        def f():
            "Some documentation."

        ensure(funk.append_to_doc).called_with(f, "Something else.").is_(f)
        ensure(f.__doc__).equals("Some documentation.\n\nSomething else.")

        mock_warn = Mock()
        with patch("warnings.warn", mock_warn):
            ensure(funk.append_to_doc).called_with(op.add, "This won't work.").is_(op.add)
            ensure(mock_warn.called).is_true()
            ensure(mock_warn.call_count).equals(1)


class around_Tests(unittest.TestCase):
    def test_should_create_around_decorators(self):
        @funk.around
        def maybe(func, value):
            if value is not None:
                return func(value)

        ensure(maybe(double)(2)).equals(4)
        ensure(maybe(double)(None)).is_none()


class after_Tests(unittest.TestCase):
    def test_should_create_after_decorators(self):
        out = []

        def run_after():
            out.append('After!')

        @funk.after(run_after)
        def something():
            out.append('Something!')
            return 5

        ensure(something).called_with().equals(5)
        ensure(out).equals(['Something!', 'After!'])


class before_Tests(unittest.TestCase):
    def test_should_create_before_decorators(self):
        out = []

        def run_before():
            out.append('Before!')

        @funk.before(run_before)
        def something():
            out.append('Something!')
            return 5

        ensure(something).called_with().equals(5)
        ensure(out).equals(['Before!', 'Something!'])


class compose_Tests(unittest.TestCase):
    def test_should_create_nested_functional_calls(self):
        fc = funk.compose(str, funk.add(2))
        ensure(fc).called_with(2).equals('4')

        fc = funk.compose(str, funk.add(2), funk.mul_by(2))
        ensure(fc).called_with(2).equals('6')


class curry_Tests(unittest.TestCase):
    def test_should_create_a_self_partialing_function(self):
        curried = funk.curry(f)
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


class debugger_Tests(unittest.TestCase):
    def test_should_start_ipdb_debugger(self):
        fake_ipdb = Mock()

        orig_import = __import__

        def fake_ipdb_import(mod, *args):
            if mod == 'ipdb':
                return fake_ipdb
            else:
                return orig_import(mod, *args)

        with patch('__builtin__.__import__', fake_ipdb_import):
            funk.debugger()
            fake_ipdb.set_trace.assert_called_once_with()

    def test_should_start_pdb_debugger(self):
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


class delete_item_Tests(unittest.TestCase):
    def test_should_update_a_deep_copy(self):
        foo = {'foo': {'bar': 'baz'}, 'blah': 5}
        ensure(funk.delete_item_on).called_with(foo, 'blah').equals({'foo': {'bar': 'baz'}})
        ensure(funk.delete_item_on).called_with(foo, 'blah').is_not(foo)
        ensure(funk.delete_item_on(foo, 'blah')['foo']).is_not(foo['foo'])


class delete_item_on_Tests(unittest.TestCase):
    def test_should_update_a_deep_copy(self):
        foo = {'foo': {'bar': 'baz'}, 'blah': 5}
        ensure(funk.delete_item).called_with('blah', foo).equals({'foo': {'bar': 'baz'}})
        ensure(funk.delete_item).called_with('blah', foo).is_not(foo)
        ensure(funk.delete_item('blah', foo)['foo']).is_not(foo['foo'])


class delete_slice_on_Tests(unittest.TestCase):
    def test_should_update_a_deep_copy(self):
        foo = ['foo', 'blah', 'bar', 'baz', ['falala']]
        ensure(funk.delete_slice_on).called_with(foo, slice(1, 2)).equals(['foo', 'bar', 'baz', ['falala']])
        ensure(funk.delete_slice_on).called_with(foo, slice(1, 2)).is_not(foo)
        ensure(funk.delete_slice_on(foo, slice(1, 2))[-1]).is_not(foo[-1])


class delete_slice_Tests(unittest.TestCase):
    def test_should_update_a_deep_copy(self):
        foo = ['foo', 'blah', 'bar', 'baz', ['falala']]
        ensure(funk.delete_slice).called_with(slice(1, 2), foo).equals(['foo', 'bar', 'baz', ['falala']])
        ensure(funk.delete_slice).called_with(slice(1, 2), foo).is_not(foo)
        ensure(funk.delete_slice(slice(1, 2), foo)[-1]).is_not(foo[-1])


class doc_Tests(unittest.TestCase):
    def test_doc_should_overwrite_a_functions_documentation(self):
        new_docs = "The new docs!"
        funk.doc(new_docs, f)
        ensure(f.__doc__).equals(new_docs)


class fluent_Tests(unittest.TestCase):
    def test_method_should_always_return_self(self):
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


class get_attr_Tests(unittest.TestCase):
    def test_should_work_like_getattr_but_with_keywords(self):
        class Foo(object): pass
        ensure(funk.get_attr).called_with('__name__', Foo).equals('Foo')
        ensure(funk.get_attr).called_with('bar', None, 5).equals(5)
        ensure(funk.get_attr).called_with('bar', None, default=5).equals(5)

    def test_from_should_work_like_getattr_but_with_keywords(self):
        class Foo(object): pass
        ensure(funk.get_attr_from).called_with(Foo, '__name__').equals('Foo')
        ensure(funk.get_attr_from).called_with(None, 'bar', 5).equals(5)
        ensure(funk.get_attr_from).called_with(None, 'bar', default=5).equals(5)


class get_item_Tests(unittest.TestCase):
    def test_should_work_like_dict_get(self):
        foo = {'foo': 'bar'}
        ensure(funk.get_item).called_with('foo', foo).equals('bar')
        ensure(funk.get_item).called_with('blah', foo, 5).equals(5)
        ensure(funk.get_item).called_with('blah', foo, default=5).equals(5)


class get_positional_arg_count_Tests(unittest.TestCase):
    def test_counts_positional_arguments(self):
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


class handle_errors_Tests(unittest.TestCase):
    def test_should_capture_exceptions(self):
        def f(arg):
            raise TypeError()

        ensure(f).called_with('foo').raises(TypeError)
        handled = funk.handle_errors(f)
        ensure(handled).called_with('foo').is_a(TypeError)

    def test_should_pass_exceptions_through(self):
        side_effect = Mock()

        def f(arg):
            side_effect()
            return 'foo'

        ensure(f).called_with(TypeError()).equals('foo')
        side_effect.assert_called_once_with()
        side_effect.reset_mock()
        handled = funk.handle_errors(f)
        ensure(handled).called_with(TypeError()).is_a(TypeError)
        ensure(side_effect.called).is_false()


class is_a_Tests(unittest.TestCase):
    def test_should_test_for_type(self):
        ensure(funk.is_a).called_with(float, 5.0).is_true()
        ensure(funk.is_a).called_with(float, 5).is_false()

        ensure(funk.is_an).called_with(int, 5).is_true()
        ensure(funk.is_an).called_with(int, 5.0).is_false()


class map_Tests(unittest.TestCase):
    def test_should_map_a_function_to_a_sequence(self):
        sequence = [1, 2, 3]
        ensure(list(funk.map(double, sequence))).equals([2, 4, 6])


class map_on_Tests(unittest.TestCase):
    def test_should_map_a_function_to_a_sequence(self):
        sequence = [1, 2, 3]
        ensure(list(funk.map_on(sequence, double))).equals([2, 4, 6])


class partial_Tests(unittest.TestCase):
    def test_should_create_a_partially_applied_function(self):
        curried = funk.partial(f)
        ensure(curried).called_with(1, 2, 3).equals((1, 2, 3))

        curried = funk.partial(f, 1)
        ensure(curried).called_with(2, 3).equals((1, 2, 3))


class pipeline_Tests(unittest.TestCase):
    def test_should_create_functional_pipelines(self):
        fc = funk.pipeline(str, funk.curry(op.add)('2'))
        ensure(fc).called_with(2).equals('22')


class provided_Tests(unittest.TestCase):
    def test_should_guard_a_function(self):
        maybe = funk.provided(lambda x: x is not None)

        ensure(maybe(double)(2)).equals(4)
        ensure(maybe(double)(None)).is_none()


class reduce_Tests(unittest.TestCase):
    def test_should_reduce_a_sequence_using_a_function(self):
        sequence = [1, 2, 3]
        ensure(funk.reduce).called_with(funk.add, sequence).equals(6)
        ensure(funk.reduce).called_with(funk.add, sequence, 6).equals(12)
        ensure(funk.reduce).called_with(funk.add, sequence, initial=6).equals(12)


class reduce_on_Tests(unittest.TestCase):
    def test_should_reduce_a_sequence_using_a_function(self):
        sequence = [1, 2, 3]
        ensure(funk.reduce_on).called_with(sequence, funk.add).equals(6)
        ensure(funk.reduce_on).called_with(sequence, funk.add, 6).equals(12)
        ensure(funk.reduce_on).called_with(sequence, funk.add, initial=6).equals(12)


class reverse_args_Tests(unittest.TestCase):
    def test_should_reverse_arguments(self):
        reversed_args = funk.reverse_args(f)

        ensure(reversed_args).called_with(1, 2, 3).equals((3, 2, 1))


class set_item_on_Tests(unittest.TestCase):
    def test_should_update_a_deep_copy(self):
        foo = {'foo': {'bar': 'baz'}}
        ensure(funk.set_item_on).called_with(foo, 'blah', 5).equals({'foo': {'bar': 'baz'}, 'blah': 5})
        ensure(funk.set_item_on).called_with(foo, 'blah', 5).is_not(foo)
        ensure(funk.set_item_on(foo, 'blah', 5)['foo']).is_not(foo['foo'])

    def test_set_item_should_update_a_deep_copy(self):
        foo = {'foo': {'bar': 'baz'}}
        ensure(funk.set_item).called_with('blah', 5, foo).equals({'foo': {'bar': 'baz'}, 'blah': 5})
        ensure(funk.set_item).called_with('blah', 5, foo).is_not(foo)
        ensure(funk.set_item('blah', 5, foo)['foo']).is_not(foo['foo'])


class set_slice_on_Tests(unittest.TestCase):
    def test_should_update_a_deep_copy(self):
        foo = ['foo', 'bar', 'baz', ['falala']]
        ensure(funk.set_slice_on).called_with(foo, slice(1, 2), ['blah']).equals(['foo', 'blah', 'baz', ['falala']])
        ensure(funk.set_slice_on).called_with(foo, slice(1, 2), ['blah']).is_not(foo)
        ensure(funk.set_slice_on(foo, slice(1, 2), ['blah'])[-1]).is_not(foo[-1])


class set_slice_Tests(unittest.TestCase):
    def test_should_update_a_deep_copy(self):
        foo = ['foo', 'bar', 'baz', ['falala']]
        ensure(funk.set_slice).called_with(slice(1, 2), ['blah'], foo).equals(['foo', 'blah', 'baz', ['falala']])
        ensure(funk.set_slice).called_with(slice(1, 2), ['blah'], foo).is_not(foo)
        ensure(funk.set_slice(slice(1, 2), ['blah'], foo)[-1]).is_not(foo[-1])


class switch_Tests(unittest.TestCase):
    def test_switch_should_pick_a_function_based_on_a_predicate(self):
        switch = funk.switch([
            (funk.is_an(int), lambda x: x ** 2),
            (funk.is_a(str), lambda x: x + x)
        ])

        ensure(switch).called_with(4).equals(16)
        ensure(switch).called_with('foo').equals('foofoo')


class wrap_Tests(unittest.TestCase):
    def test_wrap_should_simply_wrap_the_function_call(self):
        f = funk.wrap(op.add)
        ensure(f).called_with(2, 2).equals(4)
