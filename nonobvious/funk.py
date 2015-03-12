# -*- coding: utf-8 -*-
"""nonobvious.funk -- Smells like nonobvious functional combinators.
"""
import warnings
from functools import partial, wraps
import itertools
import inspect
import operator as op
import copy
import textwrap


class SENTINEL(object): pass


def debugger(*args, **kwargs):
    """Drop into the debugger.

    Uses ipdb when available, otherwise pdb.
    """
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


def append_to_doc(func, text_to_add):
    """Append the given text to the end of the function's docstring.
    """
    if func.__doc__ is None:
        docs = []
    else:
        docs = func.__doc__.split('\n', 1)

    for n, doc in enumerate(docs):
        docs[n] = textwrap.dedent(doc).rstrip()

    docs.append('\n' + textwrap.fill(text_to_add, 78))
    docs = '\n'.join(docs).strip()
    try:
        func.__doc__ = docs
    except AttributeError as e:
        warnings.warn("Could not append documentation: %s" % e.message)

    return func


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

    # Fix the docs
    doc = 'Curried function. Call with fewer positional arguments to get a partially-applied function.'
    return append_to_doc(wrapper, doc)


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


def wrap(func):
    """Return a new function that wraps the old.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def named(name, func):
    """named(name, func) -> func

    Override the __name__ of the given function.
    """
    func.__name__ = name
    return func


def doc(documentation, func):
    """doc(documentation, func) -> func

    Overrides the __doc__ method on the given function.
    """
    func.__doc__ = documentation
    return func


doc_on = named(
    "doc_on",
    doc(
        """doc_on(func, documentation) -> func

        Overrides the __doc__ method on the given function.
        """,
        reverse_args(doc)))


doc = curry(doc)


def compose(*funcs):
    """compose(*funcs) -> composed_func

    Compose the given functions, returning a function which will call each on
    the result of the next.
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
        """pipeline(*funcs) -> pipelined_func

        Arrange the given functions in a pipeline, each called on the result of the prior.
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
    """set_item_on(a_mapping, key, value) -> deepcopy_with_update

    Return a copy of the mapping with the given key and value set.
    """
    d = copy.deepcopy(a_mapping)
    d[key] = value
    return d


@curry
def set_item(key, value, a_mapping):
    """set_item(key, value, a_mapping) -> deepcopy_with_update

    Return a copy of the mapping with the given key and value set.
    """
    return set_item_on(a_mapping, key, value)


def set_slice_on(a_sequence, a_slice, values):
    """set_slice_on(a_sequence, a_slice, values) -> deepcopy_with_update

    Return a copy of the sequence with the given slice and value set.
    """
    d = copy.deepcopy(a_sequence)
    d[a_slice] = values
    return d


@curry
def set_slice(a_slice, values, a_sequence):
    """set_slice(a_slice, values, a_sequence) -> deepcopy_with_update

    Return a copy of the sequence with the given slice and value set.
    """
    return set_slice_on(a_sequence, a_slice, values)


def delete_item_on(a_mapping, key):
    """delete_item_on(a_mapping, key) -> deepcopy_with_update

    Return a copy of the mapping with the given key deleted.
    """
    d = copy.deepcopy(a_mapping)
    del d[key]
    return d


@curry
def delete_item(key, a_mapping):
    """delete_item(key, a_mapping) -> deepcopy_with_update

    Return a copy of the mapping with the given key deleted.
    """
    return delete_item_on(a_mapping, key)


def delete_slice_on(a_sequence, slice):
    """delete_slice_on(a_sequence, a_slice) -> deepcopy_with_update

    Return a copy of the sequence with the given slice deleted.
    """
    d = copy.deepcopy(a_sequence)
    del d[slice]
    return d


@curry
def delete_slice(key, a_sequence):
    """delete_slice(a_slice, a_sequence) -> deepcopy_with_update

    Return a copy of the sequence with the given slice deleted.
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

        The reverse of map(callable, sequence)
        """
    ))

map = curry(map)

_reduce = __builtins__['reduce']


def reduce(function, sequence, initial=SENTINEL):
    """reduce(function, sequence[, initial]) -> reduced_value

    Apply a function of two arguments cumulatively to the items of a sequence,
    from left to right, so as to reduce the sequence to a single value.

    >>> reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) == ((((1+2)+3)+4)+5)
    True

    If `initial` is present, it is placed before the items of the sequence in
    the calculation, and serves as a default when the sequence is empty.

    """
    return (_reduce(function, sequence)
            if initial is SENTINEL
            else _reduce(function, sequence, initial))


def reduce_on(sequence, function, initial=SENTINEL):
    """reduce_on(sequence, callable[, initial]) -> reduced_value

    The reverse of reduce(callable, sequence)
    """
    return reduce(function, sequence, initial=initial)


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


# Operations, funky style
abs = op.abs

add = curry(
    doc_on(
        reverse_args(op.add),
        """add(a, b) -> b + a
        """), 2)

and_by = curry(
    doc_on(
        reverse_args(op.and_),
        """and_by(a, b) -> b & a
        """), 2)

concat_by = curry(
    doc_on(
        wrap(op.concat),
        """concat_by(a, b) -> b + a

        For a and b sequences, concatenate to form a new sequence.
        """), 2)

contains = curry(
    doc_on(
        reverse_args(op.contains),
        """contains(a, b) -> a in b
        """), 2)

count_of = curry(
    doc_on(
        reverse_args(reverse_args(op.countOf)),
        """count_of(a, b) -> int

        Return the number of times a occurs in b.
        """), 2)

div_by = curry(
    doc_on(
        reverse_args(op.div),
        """div_by(a, b) -> b / a

        Same as b / a when __future__.division is not in effect.
        """), 2)

eq = curry(
    doc_on(
        wrap(op.eq),
        """eq(a, b) -> b == a
        """), 2)

floordiv_by = curry(
    doc_on(
        reverse_args(op.floordiv),
        """floordiv_by(a, b) -> b // a
        """), 2)

ge = curry(
    doc_on(
        reverse_args(op.ge),
        """ge(a, b) -> b >= a
        """), 2)

gt = curry(
    doc_on(
        reverse_args(op.gt),
        """gt(a, b) -> b > a
        """), 2)

is_callable = doc_on(
    wrap(op.isCallable),
    """is_callable(a) -> callable(a)

    Return True if a is callable, False otherwise.
    """)

is_mapping = doc_on(
    wrap(op.isMappingType),
    """isMappingType(a) -> isinstance(a, collections.Mapping)

    Return True if a has a mapping type, False otherwise.
    """)

is_number = doc_on(
    wrap(op.isNumberType),
    """is_number(a) -> isinstance(a, numbers.Number)

    Return True if a has a numeric type, False otherwise.
    """)

is_sequence = doc_on(
    wrap(op.isSequenceType),
    """is_sequence(a) -> isinstance(a, collections.Sequence)

    Return True if a has a sequence type, False otherwise.
    """)


@curry
def is_a(a_type, obj):
    """Check if the given object is an instance of a particular type.
    """
    return isinstance(obj, a_type)

is_an = is_a


is_exception = doc_on(
    is_an(Exception),
    """Check if the given object as in Exception.
    """
)

is_ = curry(
    doc_on(
        wrap(op.is_),
        """is_(a, b) -> b is a
        """), 2)

is_not = curry(
    doc_on(
        reverse_args(op.is_not),
        """is_not(a, b) -> b is not a
        """), 2)

le = curry(
    doc_on(
        reverse_args(op.le),
        """le(a, b) -- b <= a
        """), 2)

lshift_by = curry(
    doc_on(
        reverse_args(op.lshift),
        """lshift_by(a, b) -> b << a
        """), 2)

lt = curry(
    doc_on(
        reverse_args(op.lt),
        """lt(a, b) -> b < a
        """), 2)

method_caller = doc_on(
    wrap(op.methodcaller),
    """method_caller(name, ...) --> methodcaller object

    Return a callable object that calls the given method on its operand.
    After f = methodcaller('name'), the call f(r) returns r.name().
    After g = methodcaller('name', 'date', foo=1), the call g(r) returns
    r.name('date', foo=1).
    """)

mod_by = curry(
    doc_on(
        reverse_args(op.mod),
        """mod_by(a, b) -> b % a
        """), 2)

mul_by = curry(
    doc_on(
        reverse_args(op.mul),
        """mul_by(a, b) -> b * a.
        """), 2)

ne = curry(
    doc_on(
        reverse_args(op.ne),
        """ne(a, b) -> b != a
        """), 2)

neg = op.neg
not_ = op.not_

or_by = curry(
    doc_on(
        reverse_args(op.or_),
        """or_by(a, b) -> b | a
        """), 2)

pos = op.pos

pow_by = curry(
    doc_on(
        reverse_args(op.pow),
        """pow_by(a, b) -> b ** a.
        """), 2)

repeat_by = curry(
    doc_on(
        reverse_args(op.repeat),
        """repeat_by(a, b) -> b * a

        Return b * a, where a is an integer and b is a sequence.
        """), 2)

rshift_by = curry(
    doc_on(
        reverse_args(op.rshift),
        """rshift(a, b) -> b >> a
        """), 2)

sub_by = curry(
    doc_on(
        reverse_args(op.sub),
        """sub_by(a, b) -> b - a
        """), 2)

truediv_by = curry(
    doc_on(
        reverse_args(op.truediv),
        """truediv_by(a, b) -> b / a

        Same as a / b when __future__.division is in effect.
        """), 2)

truth = op.truth

xor_by = curry(
    doc_on(
        reverse_args(op.xor),
        """xor_by(a, b) -> b ^ a
        """), 2)
