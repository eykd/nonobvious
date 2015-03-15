# -*- coding: utf-8 -*-
"""nonobvious.nodes
"""
from collections import namedtuple

from . import funk as f


class STOP: pass


Topics = namedtuple('Topics', ('receiving', 'sending'))


@f.curry
def node(topics, func):
    """Turn a function with a single input into a microprocess generator with messaging.

    Protocol:

    1. On first yield, the node yields the topic it expects to receive messages about.
    2. It then listens for a message passed to the generator via .send(),
       passes that to the function, and yield the result of the function.

    """
    message = yield topics
    while True:
        if message is STOP:
            break
        message = yield func(message)


node.STOP = STOP
