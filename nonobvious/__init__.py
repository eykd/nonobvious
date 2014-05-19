# -*- coding: utf-8 -*-
"""nonobvious package

The first Python package to tunnel to Java!
"""
from .entities import *
from .fields import *
import valideer as V
from valideer import parse as get_validator
from valideer import accepts, adapts
from concon import frozendict, frozenlist, frozenset
