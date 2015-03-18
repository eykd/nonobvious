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


def handle_errors(func):
    """Decorator to handle errors in input or wrapped function execution.

    Implements railway-oriented "two track" programming, where pipelined or
    composed functions can handle errors from upstream. Exceptions that are
    raised inside the handler are passed downstream.

    Based on Scott Wlaschin's presentation, [Railway Oriented
    Programming--error handling in functional
    languages](https://vimeo.com/97344498).

    """
    @wraps(func)
    def wrapper(arg, **kwargs):
        if is_exception(arg):
            return arg
        else:
            try:
                return func(arg, **kwargs)
            except Exception as e:
                return e

    return wrapper


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
    doc = ('Curried function. Call with fewer positional arguments to get a '
           'partially-applied function.')
    return append_to_doc(wrapper, doc)


def reverse_args(func):
    """Return a new function with the order of arguments reversed.
    """
    expected_arg_count = get_positional_arg_count(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if expected_arg_count:
            # We only want to reverse positional arguments.
            args = (tuple(reversed(args[:expected_arg_count]))
                    + args[expected_arg_count:])
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
    """compose(func_a, func_b, func_c) -> lambda *a, **k: func_a(func_b(func_c(*a, **k)))

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

        Arrange the given functions in a pipeline, each called on the result of
        the prior.
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
        """getattr_from(obj, key[, default=value]) -> getattr(obj, key, value)
        """
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
        """get_item_from(a_dict, key[, default=value]) -> a_dict.get(key, value)
        """
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

    Also: collect(callable, seque)
    """
    return itertools.imap(function, sequence)


collect = map


def each(function, sequence):
    """each(callable, sequence) -> None

    Apply the callable to each member of the sequence. Do not save the results.
    `each` implies a function with side effects!
    """
    for item in sequence:
        function(item)


map_on = named(
    "map_on",
    doc_on(
        reverse_args(map),
        """map_on(sequence, callable) -> mapped_sequence

        The reverse of map(callable, sequence)
        """
    ))

map = curry(map)


filter = curry(filter)


_reduce = __builtins__['reduce']


@curry
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
def reduce_right(function, sequence, initial=SENTINEL):
    """reduce_right(function, sequence[, initial]) -> reduced_value

    Apply a function of two arguments cumulatively to the items of a sequence,
    from right to left, so as to reduce the sequence to a single value.

    >>> reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) == ((((5+4)+3)+2)+1)
    True

    If `initial` is present, it is placed before the items of the sequence in
    the calculation, and serves as a default when the sequence is empty.

    """
    return reduce(function, reversed(sequence), initial=initial)


def reduce_right_on(sequence, function, initial=SENTINEL):
    """reduce_right_on(sequence, callable[, initial]) -> reduced_value

    The reverse of reduce_right(callable, sequence)
    """
    return reduce_right(function, sequence, initial=initial)


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
absolute_value_of = doc_on(
    wrap(op.abs),
    """absolute_value_of(a) -> absolute value of a

    Also: abs(a)
    """
)

abs = absolute_value_of


add = curry(
    doc_on(
        reverse_args(op.add),
        """add(a, b) -> a + b

        Equivalent: add_by(b, a)
        """), 2)


add_by = curry(
    doc_on(
        wrap(op.add),
        """add(a, b) -> b + a

        Equivalent: add(b, a)
        """), 2)


and_ = curry(
    doc_on(
        wrap(op.and_),
        """and_(a, b) -> a & b
        """), 2)


and_by = curry(
    doc_on(
        reverse_args(op.and_),
        """and_by(a, b) -> b & a
        """), 2)


concat = curry(
    doc_on(
        wrap(op.concat),
        """concat(a, b) -> a + b

        For a and b sequences, concatenate to form a new sequence.

        Equivalent: concat_by(b, a)
        """), 2)


concat_by = curry(
    doc_on(
        reverse_args(op.concat),
        """concat_by(a, b) -> b + a

        For a and b sequences, concatenate to form a new sequence.

        Equivalent: concat(b, a)
        """), 2)


contains = curry(
    doc_on(
        reverse_args(op.contains),
        """contains(a, b) -> a in b

        Equivalent: contained_by(b, a)
        """), 2)


contained_by = curry(
    doc_on(
        wrap(op.contains),
        """contained_by(a, b) -> b in a

        Equivalent: contains(b, a)
        """), 2)


count_of = curry(
    doc_on(
        (reverse_args(op.countOf)),
        """count_of(a, b) -> int

        Return the number of times a occurs in b.

        Equivalent: count_in(b, a)
        """), 2)


count = count_of


count_in = curry(
    doc_on(
        wrap(op.countOf),
        """count_in(a, b) -> int

        Return the number of times b occurs in a.

        Equivalent: count_of(b, a)
        """), 2)


divide = curry(
    doc_on(
        wrap(op.div),
        """divide(a, b) -> a / b

        Same as a / b when __future__.division is not in effect.

        Also: div
        Equivalent: div_by(b, a)
        """), 2)

div = divide


divide_by = curry(
    doc_on(
        reverse_args(op.div),
        """divide_by(a, b) -> b / a

        Same as b / a when __future__.division is not in effect.

        Also: div_by
        Equivalent: div(b, a)
        """), 2)

div_by = divide_by

equal = curry(
    doc_on(
        wrap(op.eq),
        """equal(a, b) -> b == a

        Also: eq(a, b)
        """), 2)

eq = equal

floor_divide = curry(
    doc_on(
        wrap(op.floordiv),
        """floor_divide(a, b) -> b // a

        Also: floordiv(a, b)
        Equivalent: floor_divide_by(b, a)
        """), 2)

floordiv = floor_divide

floor_divide_by = curry(
    doc_on(
        reverse_args(op.floordiv),
        """floordiv_by(a, b) -> b // a

        Also: floordiv_by(a, b)
        Equivalent: floor_divide(b, a)
        """), 2)

floordiv_by = floor_divide_by

greater_than_or_equal_to = curry(
    doc_on(
        reverse_args(op.ge),
        """greater_than_or_equal_to(a, b) -> b >= a

        Also: ge(a, b)
        """), 2)

ge = greater_than_or_equal_to

greater_than = curry(
    doc_on(
        reverse_args(op.gt),
        """greater_than(a, b) -> b > a

        Also: gt(a, b)
        """), 2)

gt = greater_than

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

less_than_or_equal_to = curry(
    doc_on(
        reverse_args(op.le),
        """less_than_or_equal_to(a, b) -- b <= a

        Also: le(a, b)
        """), 2)

le = less_than_or_equal_to

left_shift = curry(
    doc_on(
        wrap(op.lshift),
        """left_shift(a, b) -> a << b

        Also: lshift(a, b)
        Equivalent: lshift_by(b, a)
        """), 2)

lshift = left_shift

left_shift_by = curry(
    doc_on(
        reverse_args(op.lshift),
        """left_shift_by(a, b) -> b << a

        Also: lshift_by(a, b)
        Equivalent: lshift(b, a)
        """), 2)

lshift_by = left_shift_by

less_than = curry(
    doc_on(
        reverse_args(op.lt),
        """less_than(a, b) -> b < a

        Also: lt(a, b)
        """), 2)

lt = less_than

method_caller = doc_on(
    wrap(op.methodcaller),
    """method_caller(name, ...) --> methodcaller object

    Return a callable object that calls the given method on its operand.
    After f = methodcaller('name'), the call f(r) returns r.name().
    After g = methodcaller('name', 'date', foo=1), the call g(r) returns
    r.name('date', foo=1).
    """)

modulus = curry(
    doc_on(
        wrap(op.mod),
        """modulus(a, b) -> a % b

        Also: mod(a, b)
        Equivalent: modulus(b, a)
        """), 2)

mod = modulus

modulus_by = curry(
    doc_on(
        reverse_args(op.mod),
        """modulus_by(a, b) -> b % a

        Also: mod_by(a, b)
        Equivalent: modulus(b, a)
        """), 2)

mod_by = modulus_by


multiply = curry(
    doc_on(
        wrap(op.mul),
        """multiply(a, b) -> a * b

        Also: mul(a, b)
        Equivalent: multiply_by(b, a)
        """), 2)

mul = multiply


multiply_by = curry(
    doc_on(
        reverse_args(op.mul),
        """multiply_by(a, b) -> b * a.

        Also: mul_by(a, b)
        Equivalent: multiply(b, a)
        """), 2)

mul_by = multiply_by

not_equal = curry(
    doc_on(
        reverse_args(op.ne),
        """not_equal(a, b) -> b != a

        Also: ne(a, b)
        """), 2)

ne = not_equal

negative = doc_on(
    wrap(op.neg),
    """negative(a) -> -a

    Also: neg(a)
    """
)

neg = negative

not_ = doc_on(
    wrap(op.not_),
    """not_(a) -> not a
    """
)

or_ = curry(
    doc_on(
        wrap(op.or_),
        """or_(a, b) -> a | b

        Equivalent: or_by(b, a)
        """), 2)

or_by = curry(
    doc_on(
        reverse_args(op.or_),
        """or_by(a, b) -> b | a

        Equivalent: or_(b, a)
        """), 2)

positive = doc_on(
    wrap(op.pos),
    """positive(a) -> +a

    Also: pos(a)
    """
)

pos = positive

power = curry(
    doc_on(
        wrap(op.pow),
        """power(a, b) -> a ** b

        Also: pow(a, b)
        Equivalent: to_the_power_of(b, a)
        """
    ), 2)

pow = power

to_the_power_of = curry(
    doc_on(
        reverse_args(op.pow),
        """to_the_power_of(a, b) -> b ** a.

        Also: pow_of(a, b)
        Equivalent: power(b, a)
        """), 2)

pow_of = to_the_power_of

repeat = curry(
    doc_on(
        wrap(op.repeat),
        """repeat(sequence, integer) -> sequence * integer

        Equivalent: repeat_by(integer, sequence)
        """), 2)

repeat_by = curry(
    doc_on(
        reverse_args(op.repeat),
        """repeat_by(integer, sequence) -> sequence * integer

        Equivalent: repeat(sequence, integer)
        """), 2)


right_shift = curry(
    doc_on(
        wrap(op.rshift),
        """right_shift(a, b) -> a >> b

        Also: rshift(a, b)
        Equivalent: right_shift_by(b, a)
        """), 2)


rshift = right_shift


right_shift_by = curry(
    doc_on(
        reverse_args(op.rshift),
        """right_shift(a, b) -> b >> a

        Also: rshift_by(a, b)
        Equivalent: right_shift(b, a)
        """), 2)


rshift_by = right_shift_by


subtract = curry(
    doc_on(
        wrap(op.sub),
        """subtract(a, b) -> a - b

        Also: sub(a, b)
        Equivalent: subtract_by(b, a)
        """), 2)

sub = subtract

subtract_by = curry(
    doc_on(
        reverse_args(op.sub),
        """subtract_by(a, b) -> b - a

        Also: sub_by(a, b)
        Equivalent: subtract(b, a)
        """), 2)

sub_by = subtract_by


truly_divide = curry(
    doc_on(
        wrap(op.truediv),
        """truly_divide(a, b) -> a / b

        Same as a / b when __future__.division is in effect.

        Also: truediv(a, b)
        Equivalent: truly_divide_by(b, a)
        """), 2)


truediv = truly_divide


truly_divide_by = curry(
    doc_on(
        reverse_args(op.truediv),
        """truly_divide_by(a, b) -> b / a

        Same as b / a when __future__.division is in effect.
        """), 2)

truediv_by = truly_divide_by


truly = doc_on(
    wrap(op.truth),
    """truly(a) -> True if a else False

    Also: truth(a)
    """
)

truth = truly


xor = curry(
    doc_on(
        wrap(op.xor),
        """xor(a, b) -> a ^ b

        Also: exclusive_or(a, b)
        Equivalent: xor_by(b, a)
        """), 2)

exclusive_or = xor

xor_by = curry(
    doc_on(
        reverse_args(op.xor),
        """xor_by(a, b) -> b ^ a

        Also: exclusive_or_by(a, b)
        Equivalent: xor(b, a)
        """), 2)

exclusive_or_by = xor_by


def switch(predicate_action_pairs):
    """Return a function which picks a function based on the result of the predicate.

    If no function is selected, return None.
    """
    def on_switch(*args, **kwargs):
        for predicate, action in predicate_action_pairs:
            if predicate(*args, **kwargs):
                return action(*args, **kwargs)

    return on_switch


filter = curry(
    doc_on(
        wrap(itertools.ifilter),
        """filter(predicate, iterable) -> filtered_iterable

        Return the stream of items for which predicate(item) is true.

        Also: select(predicate, iterable)
        """
    ), 2
)

select = filter


first = doc_on(
    compose(next, iter),
    """first(iterable) -> first_item_of_iterable

    Return the first item of the iterable.

    Also: head(iterable); take(iterable)
    """
)

head = first
take = first


find = curry(
    doc_on(
        compose(first, filter),
        """find(predicate, iterable) -> first_item_found

        Return the first item for which predicate(item) is true.
        """
    ), 2)


detect = find
