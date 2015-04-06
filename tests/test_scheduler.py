# -*- coding: utf-8 -*-
"""test_schedulers -- tests for nonobvious.scheduler
"""
from unittest import TestCase

from ensure import ensure
from mock import Mock, MagicMock, patch, call

from nonobvious import schedulers
from nonobvious import nodes
from nonobvious import funk as f


generator = type((x for x in xrange(5)))


class Scheduler(TestCase):
    def setUp(self):
        self.receive_topic = 'integers'
        self.send_topic = 'sums'
        self.node_id = 'foo'
        self.topics = nodes.Topics(self.receive_topic, self.send_topic)
        self.adder = nodes.node(self.topics, f.add(2))
        self.bus = MagicMock()

        mock_goless = self.mock_goless = Mock()

        orig_import = __import__

        def mock_goless_import(mod, *args):
            if mod == 'goless':
                return mock_goless
            else:
                return orig_import(mod, *args)

        with patch('__builtin__.__import__', mock_goless_import):
            self.scheduler = schedulers.GolessScheduler(self.bus)
            self.scheduler._get_node_id = Mock(return_value=self.node_id)

    def test_it_schedules_a_node(self):
        ensure(self.scheduler.schedule_node).called_with(self.adder).equals(self.node_id)
        self.mock_goless.go.assert_called_once_with(self.scheduler._run_node, self.adder, self.node_id)

    def test_it_starts_by_scheduling_the_message_pumps(self):
        mock_stream_factory = Mock()
        with patch.object(self.scheduler, '_get_outgoing_message_stream', mock_stream_factory):
            with patch.object(self.scheduler, '_get_incoming_message_stream', mock_stream_factory):
                self.scheduler.start()
        ensure(self.scheduler._scheduler_should_run).is_false()
        self.scheduler._stop_channel.recv.assert_called_once_with()
        ensure(self.mock_goless.go.call_count).equals(2)

        self.mock_goless.go.assert_has_calls([
            call(self.scheduler._listen_for_incoming_messages, mock_stream_factory()),
            call(self.scheduler._listen_for_outgoing_messages, mock_stream_factory()),
        ])

    def test_it_stops_by_descheduling_everything(self):
        mock_channel = self.scheduler._topic_node_id_receivers['foo']['bar'] = Mock()
        self.scheduler.stop()
        mock_channel.send.assert_called_once_with(nodes.STOP)
        self.scheduler._stop_channel.send.assert_called_once_with(None)

    def test_it_should_generate_hex_ids_from_uuid1_and_uuid4_uuids(self):
        scheduler = schedulers.GolessScheduler(MagicMock())
        ensure(scheduler._get_node_id).called_with().is_a(str)
        ensure(scheduler._get_node_id).called_with().has_length(64)

    def test_it_should_retrieve_topical_channels_for_topics_with_a_node_id(self):
        receiving_channel, sending_channel = (
            self.scheduler._get_channels_from_topics(self.topics, self.node_id)
        )

        ensure(
            receiving_channel
        ).is_(
            self.scheduler._topic_node_id_receivers[self.receive_topic][self.node_id]
        )

    def test_it_should_process_a_node_by_passing_the_received_message_and_sending_the_result(self):
        node = Mock(send=Mock(return_value=10))
        rchan = Mock(recv=Mock(return_value=5))
        schan = Mock()
        self.scheduler._receive_message_for_node_and_send_result(node, rchan, schan)
        rchan.recv.assert_called_once_with()
        node.send.assert_called_once_with(5)
        schan.send.assert_called_once_with(10)

    def test_it_should_deschedule_a_node_from_message_topics(self):
        self.scheduler._topic_node_id_receivers[self.receive_topic][self.node_id] = Mock()
        self.scheduler._topic_node_id_senders[self.send_topic][self.node_id] = Mock()

        self.scheduler.deschedule_node(self.topics, self.node_id)
        ensure(self.scheduler._topic_node_id_receivers[self.receive_topic]).does_not_contain(self.node_id)
        ensure(self.scheduler._topic_node_id_senders[self.send_topic]).does_not_contain(self.node_id)

    def test_it_should_receive_an_incoming_message_on_a_topic(self):
        receiver = self.scheduler._topic_node_id_receivers[self.receive_topic][self.node_id] = Mock()

        self.scheduler._receive_incoming_message(self.receive_topic, 'foo')

        receiver.send.assert_called_once_with('foo')

    def test_it_should_listen_for_incoming_messages(self):
        receiver = self.scheduler._topic_node_id_receivers[self.receive_topic][self.node_id] = Mock()

        self.scheduler._listen_for_incoming_messages([(self.receive_topic, 'foo')])

        receiver.send.assert_called_once_with('foo')

    def test_it_should_send_an_outgoing_message(self):
        self.scheduler._send_outgoing_message(self.send_topic, 'foo')
        self.bus[self.send_topic].send.assert_called_once_with('foo')

    def test_it_should_listen_for_outgoing_messages(self):
        self.scheduler._listen_for_outgoing_messages([(self.send_topic, 'foo')])
        self.bus[self.send_topic].send.assert_called_once_with('foo')
