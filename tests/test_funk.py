# -*- coding: utf-8 -*-
"""Tests for nonobvious.events
"""
import sys
import unittest

import operator as op
import functools

from ensure import ensure
from mock import Mock, patch, call
from nose.plugins.attrib import attr

from nonobvious import funk


def f(*args):
    return args


def double(x):
    return x * 2


class abs_Tests(unittest.TestCase):
    def test_should_return_the_absolute_value_of(self):
        for name in ('absolute_value_of', 'abs'):
            abs = getattr(funk, name)
            ensure(abs).called_with(-5).equals(5)
            ensure(abs).called_with(5).equals(5)


class add_Tests(unittest.TestCase):
    def test_add_should_add_numbers(self):
        for name in ('add', 'add_by'):
            add = getattr(funk, name)
            ensure(add).called_with(5, 5).equals(10)


class and__Tests(unittest.TestCase):
    def test_and__should_(self):
        for name in ('and_', ):
            and_ = getattr(funk, name)
            ensure(and_).called_with(5, 10).equals(5 & 10)


class and_by_Tests(unittest.TestCase):
    def test_and_by_should_(self):
        for name in ('and_by', ):
            and_by = getattr(funk, name)
            ensure(and_by).called_with(5, 10).equals(10 & 5)



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


class concat_Tests(unittest.TestCase):
    def test_concat_should_(self):
        for name in ('concat', ):
            concat = getattr(funk, name)
            ensure(concat).called_with([5], [6]).equals([5, 6])


class concat_by_Tests(unittest.TestCase):
    def test_concat_by_should_(self):
        for name in ('concat_by', ):
            concat_by = getattr(funk, name)
            ensure(concat_by).called_with([5], [10]).equals([10, 5])


class contains_Tests(unittest.TestCase):
    def test_contains_should_(self):
        for name in ('contains', ):
            contains = getattr(funk, name)
            ensure(contains).called_with(5, [10, 5]).is_true()
            ensure(contains).called_with(4, [10, 5]).is_false()


class contained_by_Tests(unittest.TestCase):
    def test_contained_by_should_(self):
        for name in ('contained_by', ):
            contained_by = getattr(funk, name)
            ensure(contained_by).called_with([10, 5], 5).is_true()
            ensure(contained_by).called_with([10, 5], 6).is_false()


class count_of_Tests(unittest.TestCase):
    def test_count_of_should_(self):
        for name in ('count_of', 'count'):
            count_of = getattr(funk, name)
            ensure(count_of).called_with('o', 'foo').equals(2)


class count_in_Tests(unittest.TestCase):
    def test_count_in_should_(self):
        for name in ('count_in', ):
            count_in = getattr(funk, name)
            ensure(count_in).called_with('foo', 'o').equals(2)


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


class divide_Tests(unittest.TestCase):
    def test_divide_should_(self):
        for name in ('divide', 'div'):
            divide = getattr(funk, name)
            ensure(divide).called_with(10, 5).equals(10 / 5)


class divide_by_Tests(unittest.TestCase):
    def test_divide_by_should_(self):
        for name in ('divide_by', 'div_by'):
            divide_by = getattr(funk, name)
            ensure(divide_by).called_with(5, 10).equals(10 / 5)


class doc_Tests(unittest.TestCase):
    def test_doc_should_overwrite_a_functions_documentation(self):
        new_docs = "The new docs!"
        funk.doc(new_docs, f)
        ensure(f.__doc__).equals(new_docs)


class equal_Tests(unittest.TestCase):
    def test_equal_should_(self):
        for name in ('equal', 'eq'):
            equal = getattr(funk, name)
            ensure(equal).called_with(5, 5).is_true()


class each_Tests(unittest.TestCase):
    def test_should_call_func_on_each_member_of_iterable(self):
        caller = Mock()
        funk.each(caller, [1, 2, 3])
        caller.assert_calls([
            call(1),
            call(2),
            call(3),
        ])


class floor_divide_Tests(unittest.TestCase):
    def test_floor_divide_should_(self):
        for name in ('floor_divide', 'floordiv'):
            floor_divide = getattr(funk, name)
            ensure(floor_divide).called_with(11, 5).equals(11 // 5)


class floor_divide_by_Tests(unittest.TestCase):
    def test_floor_divide_by_should_(self):
        for name in ('floor_divide_by', ):
            floor_divide_by = getattr(funk, name)
            ensure(floor_divide_by).called_with(5, 11).equals(11 // 5)


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


class greater_than_or_equal_to_Tests(unittest.TestCase):
    def test_greater_than_or_equal_to_should_(self):
        for name in ('greater_than_or_equal_to', 'ge'):
            greater_than_or_equal_to = getattr(funk, name)
            ensure(greater_than_or_equal_to).called_with(5, 5).equals(5 >= 5)
            ensure(greater_than_or_equal_to).called_with(5, 10).equals(10 >= 5)
            ensure(greater_than_or_equal_to).called_with(5, 4).equals(4 >= 5)


class greater_than_Tests(unittest.TestCase):
    def test_greater_than_should_(self):
        for name in ('greater_than', 'gt'):
            greater_than = getattr(funk, name)
            ensure(greater_than).called_with(5, 5).equals(5 > 5)
            ensure(greater_than).called_with(5, 6).equals(6 > 5)
            ensure(greater_than).called_with(6, 5).equals(5 > 6)


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


class is__Tests(unittest.TestCase):
    def test_is__should_(self):
        for name in ('is_', ):
            is_ = getattr(funk, name)
            ensure(is_).called_with(f, f).is_true()


class is_a_Tests(unittest.TestCase):
    def test_should_test_for_type(self):
        for name in ('is_a', 'is_an'):
            is_a = getattr(funk, name)
            ensure(is_a).called_with(float, 5.0).is_true()
            ensure(is_a).called_with(float, 5).is_false()


class is_callable_Tests(unittest.TestCase):
    def test_is_callable_should_(self):
        for name in ('is_callable', ):
            is_callable = getattr(funk, name)
            ensure(is_callable).called_with(Mock()).is_true()
            ensure(is_callable).called_with(None).is_false()


class is_mapping_Tests(unittest.TestCase):
    def test_is_mapping_should_(self):
        for name in ('is_mapping', ):
            is_mapping = getattr(funk, name)
            ensure(is_mapping).called_with({}).is_true()
            ensure(is_mapping).called_with([]).is_false()


class is_not_Tests(unittest.TestCase):
    def test_is_not_should_(self):
        for name in ('is_not', ):
            is_not = getattr(funk, name)
            ensure(is_not).called_with(f, double).is_true()


class is_number_Tests(unittest.TestCase):
    def test_is_number_should_(self):
        for name in ('is_number', ):
            is_number = getattr(funk, name)
            ensure(is_number).called_with(5).is_true()
            ensure(is_number).called_with(5.0).is_true()
            ensure(is_number).called_with('5').is_false()


class is_sequence_Tests(unittest.TestCase):
    def test_is_sequence_should_(self):
        for name in ('is_sequence', ):
            is_sequence = getattr(funk, name)
            ensure(is_sequence).called_with([]).is_true()
            ensure(is_sequence).called_with({}).is_false()
            ensure(is_sequence).called_with(None).is_false()


class less_than_Tests(unittest.TestCase):
    def test_less_than_should_(self):
        for name in ('less_than', 'lt'):
            less_than = getattr(funk, name)
            ensure(less_than).called_with(5, 5).equals(5 < 5)
            ensure(less_than).called_with(5, 10).equals(10 < 5)
            ensure(less_than).called_with(10, 5).equals(5 < 10)


class less_than_or_equal_to_Tests(unittest.TestCase):
    def test_less_than_or_equal_to_should_(self):
        for name in ('less_than_or_equal_to', 'le'):
            less_than_or_equal_to = getattr(funk, name)
            ensure(less_than_or_equal_to).called_with(5, 5).equals(5 <= 5)
            ensure(less_than_or_equal_to).called_with(10, 5).equals(5 <= 10)
            ensure(less_than_or_equal_to).called_with(5, 10).equals(10 <= 5)


class lshift_Tests(unittest.TestCase):
    def test_lshift_should_(self):
        for name in ('left_shift', 'lshift'):
            lshift = getattr(funk, name)
            ensure(lshift).called_with(5, 10).equals(5 << 10)


class lshift_by_Tests(unittest.TestCase):
    def test_lshift_by_should_(self):
        for name in ('left_shift_by', 'lshift_by'):
            lshift_by = getattr(funk, name)
            ensure(lshift_by).called_with(5, 10).equals(10 << 5)


class map_Tests(unittest.TestCase):
    def test_should_map_a_function_to_a_sequence(self):
        sequence = [1, 2, 3]
        ensure(list(funk.map(double, sequence))).equals([2, 4, 6])


class map_on_Tests(unittest.TestCase):
    def test_should_map_a_function_to_a_sequence(self):
        sequence = [1, 2, 3]
        ensure(list(funk.map_on(sequence, double))).equals([2, 4, 6])


class method_caller_Tests(unittest.TestCase):
    def test_method_caller_should_(self):
        for name in ('method_caller', ):
            method_caller = getattr(funk, name)
            mocked = Mock()
            method_caller('foo')(mocked)
            mocked.foo.assert_called_once_with()

            method_caller('bar', 1, 2, three='four')(mocked)
            mocked.bar.assert_called_once_with(1, 2, three='four')


class mod_Tests(unittest.TestCase):
    def test_mod_should_(self):
        for name in ('modulus', 'mod'):
            mod = getattr(funk, name)
            ensure(mod).called_with(11, 5).equals(11 % 5)


class modulus_by_Tests(unittest.TestCase):
    def test_modulus_by_should_(self):
        for name in ('modulus_by', 'mod_by'):
            modulus_by = getattr(funk, name)
            ensure(modulus_by).called_with(5, 11).equals(11 % 5)


class multiply_Tests(unittest.TestCase):
    def test_multiply_should_(self):
        for name in ('multiply', 'mul'):
            multiply = getattr(funk, name)
            ensure(multiply).called_with(10, 5).equals(10 * 5)


class multiply_by_Tests(unittest.TestCase):
    def test_multiply_by_should_(self):
        for name in ('multiply_by', 'mul_by'):
            multiply_by = getattr(funk, name)
            ensure(multiply_by).called_with(5, 10).equals(10 * 5)


class negative_Tests(unittest.TestCase):
    def test_negative_should_(self):
        for name in ('negative', 'neg'):
            negative = getattr(funk, name)
            ensure(negative).called_with(5).equals(-5)


class not__Tests(unittest.TestCase):
    def test_not__should_(self):
        for name in ('not_', ):
            not_ = getattr(funk, name)
            ensure(not_).called_with(True).is_false()
            ensure(not_).called_with(False).is_true()


class not_equal_Tests(unittest.TestCase):
    def test_not_equal_should_(self):
        for name in ('not_equal', ):
            not_equal = getattr(funk, name)
            ensure(not_equal).called_with(5, 5).is_false()
            ensure(not_equal).called_with(10, 5).is_true()


class or__Tests(unittest.TestCase):
    def test_or__should_(self):
        for name in ('or_', ):
            or_ = getattr(funk, name)
            ensure(or_).called_with(10, 5).equals(10 | 5)


class or_by_Tests(unittest.TestCase):
    def test_or_by_should_(self):
        for name in ('or_by', ):
            or_by = getattr(funk, name)
            ensure(or_by).called_with(5, 10).equals(10 | 5)


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


class positive_Tests(unittest.TestCase):
    def test_positive_should_(self):
        for name in ('positive', 'pos'):
            positive = getattr(funk, name)
            ensure(positive).called_with(5).equals(+5)


class power_Tests(unittest.TestCase):
    def test_power_should_(self):
        for name in ('power', 'pow'):
            power = getattr(funk, name)
            ensure(power).called_with(5, 2).equals(5 ** 2)


class to_the_power_of_Tests(unittest.TestCase):
    def test_to_the_power_of_should_(self):
        for name in ('to_the_power_of', 'pow_of'):
            to_the_power_of = getattr(funk, name)
            ensure(to_the_power_of).called_with(2, 5).equals(5 ** 2)


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

        sequence = [[0, 1], [2, 3], [4, 5]]
        ensure(funk.reduce).called_with(
            funk.concat, sequence, initial=[]
        ).equals([0, 1, 2, 3, 4, 5])


class reduce_on_Tests(unittest.TestCase):
    def test_should_reduce_a_sequence_using_a_function(self):
        sequence = [1, 2, 3]
        ensure(funk.reduce_on).called_with(sequence, funk.add).equals(6)
        ensure(funk.reduce_on).called_with(sequence, funk.add, 6).equals(12)
        ensure(funk.reduce_on).called_with(sequence, funk.add, initial=6).equals(12)

        sequence = [[0, 1], [2, 3], [4, 5]]
        ensure(funk.reduce_on).called_with(
            sequence, funk.concat, initial=[]
        ).equals([0, 1, 2, 3, 4, 5])


class reduce_right_Tests(unittest.TestCase):
    def test_should_right_associatively_reduce_a_sequence_using_a_function(self):
        sequence = [1, 2, 3]
        ensure(funk.reduce_right).called_with(funk.add, sequence).equals(6)
        ensure(funk.reduce_right).called_with(funk.add, sequence, 6).equals(12)
        ensure(funk.reduce_right).called_with(funk.add, sequence, initial=6).equals(12)

        sequence = [[0, 1], [2, 3], [4, 5]]
        ensure(funk.reduce_right).called_with(
            funk.concat, sequence, initial=[]
        ).equals([4, 5, 2, 3, 0, 1])


class reduce_right_on_Tests(unittest.TestCase):
    def test_should_right_associatively_reduce_a_sequence_using_a_function(self):
        sequence = [1, 2, 3]
        ensure(funk.reduce_right_on).called_with(sequence, funk.add).equals(6)
        ensure(funk.reduce_right_on).called_with(sequence, funk.add, 6).equals(12)
        ensure(funk.reduce_right_on).called_with(sequence, funk.add, initial=6).equals(12)

        sequence = [[0, 1], [2, 3], [4, 5]]
        ensure(funk.reduce_right_on).called_with(
            sequence, funk.concat, initial=[]
        ).equals([4, 5, 2, 3, 0, 1])


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
