nonobvious
==========

The first python package to jump across the English Channel!

.. image:: https://travis-ci.org/eykd/nonobvious.svg?branch=master
    :target: https://travis-ci.org/eykd/nonobvious

.. image:: https://coveralls.io/repos/eykd/nonobvious/badge.png
  :target: https://coveralls.io/r/eykd/nonobvious


This package attempts to implement the "functional core, imperative shell"
pattern described in `Gary Bernhardt's talk on Boundaries`_, using some ideas
found in the Ruby `obvious`_ project.

.. _Gary Bernhardt's talk on Boundaries: https://www.destroyallsoftware.com/talks/boundaries
.. _obvious: http://obvious.retromocha.com/


Functional Core, Imperative Shell
---------------------------------

The basic idea is that your core domain model implements business logic using
functional techniques, with immutable values and copy-on-write. The functional
core is wrapped by an imperative shell which drives the core models and
interacts across the boundary with the outside world through "primitive"
values. The immutable domain models can be easily converted to primitive data
structures whose state has no affect on the immutable core.

``nonobvious.models`` and ``nonobvious.fields`` provide a declarative modeling
language, similar to Django's model objects, but without an ORM. We can easily
use validators and adaptors from the ``valideer`` project to ensure that the
models are always in a valid state and can easily be constructed from standard
python data structures.

By making use of ``concon.frozendict``, ``concon.frozenlist``, and
``concon.frozenset`` within model adaptors allows us to model complex data
structures guaranteed to be correctly formed at all times.

As for the imperative shell, at present, you're on your own!
