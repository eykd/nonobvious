# -*- coding: utf-8 -*-
"""nonobvious.scheduler
"""
import logging
from collections import defaultdict
import uuid

from nonobvious import nodes

logger = logging.getLogger('nonobvious.scheduler')


class GolessScheduler(object):
    """Scheduler for scheduling nodes via goless. Requires `goless` package.

    Goless documentation: https://goless.readthedocs.org
    """
    def __init__(self, message_bus):
        import goless
        self._goless = goless
        self.message_bus = message_bus
        self.reset()

    def reset(self):
        """Reset the scheduler.

        Please be sure the scheduler has stopped before resetting it!
        """
        self._topic_node_id_receivers = defaultdict(lambda: defaultdict(self._make_channel))
        self._topic_node_id_senders = defaultdict(lambda: defaultdict(self._make_channel))

        self._stop_channel = self._goless.chan()
        self._scheduler_should_run = True

    def start(self):
        """Schedule the message pumps to listen for incoming and outgoing messages.
        """
        self._scheduler_should_run = True
        self._goless.go(self._listen_for_incoming_messages, self._get_incoming_message_stream())
        self._goless.go(self._listen_for_outgoing_messages, self._get_outgoing_message_stream())
        self._stop_channel.recv()
        self._scheduler_should_run = False

    def stop(self):
        """Wind down and stop all scheduled nodes and message pumps.
        """
        for topic in self._topic_node_id_receivers.itervalues():
            for channel in topic.itervalues():
                channel.send(nodes.STOP)
        self._stop_channel.send(None)

    def schedule_node(self, node):
        """Schedule the node to run with goless.
        """
        node_id = self._get_node_id()

        self._goless.go(self._run_node, node, node_id)

        return node_id

    def _make_channel(self):
        return self._goless.chan(-1)

    def _get_node_id(self):
        """Return a unique hexadecimal ID.

        To ensure a unique ID for nodes scheduled within the same moment of
        time, we'll use the hexadecimal digest of a UUID1 concatenated with the
        hexadecimal digest of a UUID4.
        """
        return uuid.uuid1().get_hex() + uuid.uuid4().get_hex()

    def _get_channels_from_topics(self, topics, node_id):
        receive_topic, send_topic = topics
        receiving_channel = self._topic_node_id_receivers[receive_topic][node_id]
        sending_channel = self._topic_node_id_senders[send_topic][node_id]
        return receiving_channel, sending_channel

    def _receive_message_for_node_and_send_result(self, node, receiving_channel, sending_channel):
        message = receiving_channel.recv()
        result = node.send(message)
        sending_channel.send(result)

    def deschedule_node(self, topics, node_id):
        """Remove the given node ID from the given receive/send topics.
        """
        self._topic_node_id_receivers[topics.receiving].pop(node_id, None)
        self._topic_node_id_senders[topics.sending].pop(node_id, None)

    def _run_node(self, node, node_id):  # pragma: no cover
        """Run the node, feeding messages to and from the node to its channels.
        """
        topics = node.next()
        receiving_channel, sending_channel = self._get_channels_from_topics(topics, node_id)

        while self._scheduler_should_run:
            try:
                self._receive_message_for_node_and_send_result(node, receiving_channel, sending_channel)
            except:
                logger.exception("Exception occurred in node %s with id %s.", node, node_id)
                break

        self.deschedule_node(self, topics, node_id)

    def _get_incoming_message_stream(self):  # pragma: no cover
        while self._scheduler_should_run:
            for topic in self._topic_node_id_receivers.iterkeys():
                yield topic, self.message_bus[topic].recv()

    def _receive_incoming_message(self, topic, message):
        for channel in self._topic_node_id_receivers[topic].itervalues():
            channel.send(message)

    def _listen_for_incoming_messages(self, topics_messages):
        for topic, message in topics_messages:
            self._receive_incoming_message(topic, message)

    def _send_outgoing_message(self, topic, message):
        self.message_bus[topic].send(message)

    def _get_outgoing_message_stream(self):  # pragma: no cover
        while self._scheduler_should_run:
            for topic, senders in self._topic_node_id_senders.iteritems():
                for channel in senders.itervalues():
                    yield topic, channel.recv()

    def _listen_for_outgoing_messages(self, topics_messages):
        for topic, message in topics_messages:
            self._send_outgoing_message(topic, message)
