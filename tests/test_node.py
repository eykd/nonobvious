# -*- coding: utf-8 -*-
"""test_node -- tests for nonobvious.node
"""
from unittest import TestCase

from ensure import ensure
from mock import Mock, patch

from nonobvious import nodes
from nonobvious import funk as f


generator = type((x for x in xrange(5)))


class Node(TestCase):
    def setUp(self):
        self.receive_topic = 'integers'
        self.send_topic = 'sums'
        self.topics = nodes.Topics(self.receive_topic, self.send_topic)
        self.adder = nodes.node(self.topics, f.add(2))

    def test_it_creates_a_generator(self):
        ensure(self.adder).is_a(generator)

    def test_it_returns_the_topic_on_first_yield(self):
        ensure(self.adder.next).called_with().equals(self.topics)

    def test_it_returns_the_function_result_on_subsequent_yields(self):
        self.adder.next()
        ensure(self.adder.send).called_with(2).equals(4)

    def test_it_raises_StopIteration_when_passed_a_stop_message(self):
        self.adder.next()
        ensure(self.adder.send).called_with(nodes.node.STOP).raises(StopIteration)

    def test_it_is_curriable(self):
        topic_node = nodes.node(self.topics)
        ensure(topic_node).called_with(f.add(2)).is_a(generator)
        ensure(topic_node(f.add(2)).next).called_with().equals(self.topics)
