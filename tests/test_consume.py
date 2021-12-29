import unittest
from moto import mock_sqs

from aws_sqs_consumer import Consumer
from .utils import async_sqs


class TestConsumeMessage(unittest.TestCase):
    @mock_sqs
    def test_single_message_consume(self):
        messages = []

        class TestConsumer(Consumer):
            def handle_message(self, message):
                messages.append(message.Body)

        with async_sqs(TestConsumer) as (sqs_client, queue):
            sqs_client.send_message(
                QueueUrl=queue["QueueUrl"],
                MessageBody="test_message"
            )

        assert messages[0] == "test_message"
