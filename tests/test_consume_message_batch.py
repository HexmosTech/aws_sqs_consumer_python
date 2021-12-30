import unittest
from moto import mock_sqs
from typing import List

from aws_sqs_consumer import Consumer, Message
from .utils import async_sqs


class TestConsumeMessageBatch(unittest.TestCase):
    @mock_sqs
    def test_message_batch_consume_body(self):
        message_batches = []

        class TestBatchConsumer(Consumer):
            def handle_message_batch(self, message_batch: List[Message]):
                message_batches.append([message.Body for message in message_batch])

        with async_sqs(TestBatchConsumer, batch_size=5) as (sqs_client, queue):
            # Send 24 messages in batches of [10, 10, 4]
            entries = [
                { "Id": f"m{i}", "MessageBody": f"test message {i}" }
                for i in range(24)
            ]
            sqs_client.send_message_batch(
                QueueUrl=queue["QueueUrl"],
                Entries=entries[:10]
            )
            sqs_client.send_message_batch(
                QueueUrl=queue["QueueUrl"],
                Entries=entries[10:20]
            )
            sqs_client.send_message_batch(
                QueueUrl=queue["QueueUrl"],
                Entries=entries[20:]
            )

        # There should be minimum of 24//5=5 batches
        self.assertGreaterEqual(len(message_batches), 5)
        
        # Maximum of the all batches should be 5
        self.assertEqual(len(max(message_batches, key=len)), 5)

        # Total messages across all batches should be 24
        self.assertEqual(sum([len(b) for b in message_batches]), 24)

    @mock_sqs
    def test_message_batch_handle_exception(self):
        exceptions = []

        class TestBatchConsumer(Consumer):
            def handle_message_batch(self, message_batch: List[Message]):
                raise Exception("Failed to handle message batch")

            def handle_batch_processing_exception(self, messages: List[Message], exception):
                exceptions.append(exception)

        with async_sqs(TestBatchConsumer, batch_size=5) as (sqs_client, queue):
            sqs_client.send_message(
                QueueUrl=queue["QueueUrl"],
                MessageBody="test_message"
            )

        self.assertEqual(len(exceptions), 1)
        self.assertEqual(type(exceptions[0]), Exception)
        self.assertEqual(str(exceptions[0]), "Failed to handle message batch")
