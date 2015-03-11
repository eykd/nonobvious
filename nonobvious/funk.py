# -*- coding: utf-8 -*-
"""nonobvious.funk -- Smells like nonobvious functional combinators.
"""
from functools import partial, wraps
import itertools
import inspect
import operator as op
import copy


class SENTINEL(object): pass


def debugger(*args, **kwargs):
    try:
        import ipdb as pdb
    except ImportError:
        import pdb as pdb
    pdb.set_trace()


def get_positional_arg_count(func):
    """Return the expected positional argument count for the function.
    """
    try:
        argspec = inspect.getargspec(func)
    except TypeError:
        return None
    else:
        count = len(argspec.args)
        if argspec.defaults is not None:
            count -= len(argspec.defaults)
        return count


def curry(func, expected_arg_count=None):
    """Return a self-partialing function.

    The next call to the returned function returns a partially-applied function
    with the given arguments.

    For non-Python functions, the expected number of args can be passed, e.g.:

    >>> import operator
    >>> curry(2, operator.add)

    """
    if expected_arg_count is None:
        expected_arg_count = get_positional_arg_count(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if expected_arg_count and len(args) >= expected_arg_count:
            return func(*args, **kwargs)
        else:
            return partial(func, *args, **kwargs)

    return wrapper


def reverse_args(func):
    """Return a new function with the order of arguments reversed.
    """
    expected_arg_count = get_positional_arg_count(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if expected_arg_count:
            # We only want to reverse positional arguments.
            args = tuple(reversed(args[:expected_arg_count])) + args[expected_arg_count:]
            return func(*args, **kwargs)
        else:
            return func(*reversed(args), **kwargs)

    return wrapper


def named(name, func):
    """Override the __name__ of the given function.
    """
    func.__name__ = name
    return func


def doc(documentation, func):
    """Override the __doc__ method on the given function.
    """
    func.__doc__ = documentation
    return func


doc_on = named("doc_on", reverse_args(doc))


doc = curry(doc)


def compose(*funcs):
    """Compose the given functions, calling each on the result of the next.
    """
    if len(funcs) > 2:
        return compose(funcs[0], compose(*funcs[1:]))
    else:
        def composed(*args, **kwargs):
            return funcs[0](funcs[1](*args, **kwargs))

        return composed


pipeline = named(
    'pipeline',
    doc_on(
        reverse_args(compose),
        """Arrange the given functions in a pipeline, each called on the result of the prior.
        """
    ))


def get_attr(attr, obj, default=SENTINEL):
    """get_attr(attr, obj[, default=value]) -> getattr(obj, attr, value)
    """
    return (getattr(obj, attr)
            if default is SENTINEL
            else getattr(obj, attr, default))


get_attr_from = named(
    "get_attr_from",
    doc_on(
        reverse_args(get_attr),
        """getattr_from(obj, key[, default=value]) -> getattr(obj, key, value)"""
    ))


get_attr = curry(get_attr)


def get_item(key, a_dict, default=None):
    """get_item(key, a_dict[, default=value]) -> a_dict.get(key, value)
    """
    return a_dict.get(key, default)


get_item_from = named(
    "get_item_from",
    doc_on(
        reverse_args(get_item),
        """get_item_from(a_dict, key[, default=value]) -> a_dict.get(key, value)"""
    ))


get_item = curry(get_item)


def set_item_on(a_mapping, key, value):
    """Return a copy of the mapping with the given key and value set.
    """
    d = copy.deepcopy(a_mapping)
    d[key] = value
    return d


@curry
def set_item(key, value, a_mapping):
    """Return a copy of the mapping with the given key and value set.
    """
    return set_item_on(a_mapping, key, value)


def set_slice_on(a_sequence, slice, value):
    """Return a copy of the sequence with the given slice and value set.
    """
    d = copy.deepcopy(a_sequence)
    d[slice] = value
    return d


@curry
def set_slice(key, value, a_sequence):
    """Return a copy of the sequence with the given slice and value set.
    """
    return set_slice_on(a_sequence, key, value)


def delete_item_on(a_mapping, key):
    """Return a copy of the mapping with the given key deleted.
    """
    d = copy.deepcopy(a_mapping)
    del d[key]
    return d


@curry
def delete_item(key, a_mapping):
    """Return a copy of the mapping with the given key deleted.
    """
    return delete_item_on(a_mapping, key)


def delete_slice_on(a_sequence, slice):
    """Return a copy of the sequence with the given slice deleted.
    """
    d = copy.deepcopy(a_sequence)
    del d[slice]
    return d


@curry
def delete_slice(key, a_sequence):
    """Return a copy of the sequence with the given slice deleted.
    """
    return delete_slice_on(a_sequence, key)


def map(function, sequence):
    """map(callable, sequence) -> mapped_sequence

    For each item in the given sequence, provide the item to the callable as
    the sole argument, and return the resulting value in the resulting mapped
    sequence.
    """
    return itertools.imap(function, sequence)


map_on = named(
    "map_on",
    doc_on(
        reverse_args(map),
        """map_on(sequence, callable) -> mapped_sequence

        The inverse of map(callable, sequence)
        """
    ))

map = curry(map)


@doc(reduce.__doc__)
def reduce(function, sequence, initial=SENTINEL):
    return (reduce(function, sequence)
            if initial is SENTINEL
            else reduce(function, sequence, initial))


reduce_on = named(
    "reduce_on",
    doc_on(
        reverse_args(reduce),
        """reduce_on(sequence, callable[, initial]) -> reduced_value

        The inverse of reduce(callable, sequence)
        """
    ))


@curry
def before(before_func, func):
    """Curried decorator to create run-a-function-before-this-one decorators.

    Example:

    >>> def run_before():
    ...     print "Before!"

    >>> @before(run_before)
    ... def do_something():
    ...     print "Something!"

    >>> do_something()
    Before!
    Something!
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        before_func(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapped


@curry
def after(after_func, func):
    """Curried decorator to create run-a-function-after-this-one decorators.

    Example:

    >>> def run_after():
    ...     print "After!"

    >>> @after(run_after)
    ... def do_something():
    ...     print "Something!"

    >>> do_something()
    Something!
    After!
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        result = func()
        after_func(*args, **kwargs)
        return result
    return wrapped


@curry
def around(wrapping_func, func):
    """Curried decorator to create a wrapping function decorator.

    Example:

    >>> def double(x):
    ...    return x * 2

    >>> @around
    ... def maybe(func, value):
    ...     if value is not None:
    ...         return func(value)
    ...     else:
    ...         return "Nope."

    >>> maybe(double)(2)
    4
    >>> maybe(double)(None)
    "Nope."
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        return wrapping_func(func, *args, **kwargs)
    return wrapped


def provided(guard):
    """"""
    @around
    def wrapped(func, *args, **kwargs):
        if guard(*args, **kwargs):
            return func(*args, **kwargs)
    return wrapped


# Method decorators
def fluent(meth):
    """Decorated method always returns self.
    """
    @wraps(meth)
    def wrapped(self, *args, **kwargs):
        meth(self, *args, **kwargs)
        return self

    return wrapped


# Operations
abs = op.abs
add = curry(reverse_args(op.add), 2)
and_ = curry(reverse_args(op.and_), 2)
concat = curry(op.concat, 2)
contains = curry(reverse_args(op.contains), 2)
count_of = curry(reverse_args(reverse_args(op.countOf)), 2)
div_by = curry(reverse_args(op.div), 2)
eq = curry(op.eq, 2)
floordiv_by = curry(reverse_args(op.floordiv), 2)
ge = curry(reverse_args(op.ge), 2)
gt = curry(reverse_args(op.gt), 2)
is_callable = op.isCallable
is_mapping_type = op.isMappingType
is_number_type = op.isNumberType
is_sequence_type = op.isSequenceType
is_ = curry(op.is_, 2)
is_not = curry(reverse_args(op.is_not), 2)
le = curry(reverse_args(op.le), 2)
lshift_by = curry(reverse_args(op.lshift), 2)
lt = curry(reverse_args(op.lt), 2)
method_caller = op.methodcaller
mod_by = curry(reverse_args(op.mod), 2)
mul_by = curry(reverse_args(op.mul), 2)
ne = curry(reverse_args(op.ne), 2)
neg = op.neg
not_ = op.not_
or_ = curry(reverse_args(op.or_), 2)
pos = op.pos
pow = curry(reverse_args(op.pow), 2)
repeat = curry(reverse_args(op.repeat), 2)
rshift_by = curry(reverse_args(op.rshift), 2)
sub_by = curry(reverse_args(op.sub), 2)
truediv_by = curry(reverse_args(op.truediv), 2)
truth = op.truth
xor = curry(reverse_args(op.xor), 2)
