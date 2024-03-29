import unittest

from aws_sqs_consumer import Consumer, Message
import os


class SimpleSQSConsumer(Consumer):
    def handle_message(self, message: Message):
        pass


class TestConsumerAttributes(unittest.TestCase):
    def setUp(self) -> None:
        self.queue_url = \
            "https://eu-west-1.queue.amazonaws.com/123456789012/test_queue"

    def test_mandatory_queue_url(self):
        with self.assertRaisesRegex(TypeError, "queue_url"):
            SimpleSQSConsumer()

    def test_default_attributes(self):
        os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
        consumer = SimpleSQSConsumer(queue_url=self.queue_url)
        self.assertEqual(consumer.queue_url, self.queue_url)
        self.assertEqual(consumer.attribute_names, [])
        self.assertEqual(consumer.message_attribute_names, [])
        self.assertEqual(consumer.batch_size, 1)
        self.assertEqual(consumer.wait_time_seconds, 1)
        self.assertEqual(consumer.visibility_timeout_seconds, None)
        self.assertEqual(consumer.polling_wait_time_ms, 0)

    def test_all_attributes(self):
        consumer = SimpleSQSConsumer(
            queue_url=self.queue_url,
            attribute_names=[
                "ApproximateFirstReceiveTimestamp", "MaximumMessageSize"
            ],
            message_attribute_names=["attr1", "attr2"],
            batch_size=5,
            wait_time_seconds=10,
            visibility_timeout_seconds=30,
            polling_wait_time_ms=1000,
            region="us-west-2"
        )
        self.assertEqual(consumer.queue_url, self.queue_url)
        self.assertEqual(
            consumer.attribute_names,
            ["ApproximateFirstReceiveTimestamp", "MaximumMessageSize"]
        )
        self.assertEqual(consumer.message_attribute_names, ["attr1", "attr2"])
        self.assertEqual(consumer.batch_size, 5)
        self.assertEqual(consumer.wait_time_seconds, 10)
        self.assertEqual(consumer.visibility_timeout_seconds, 30)
        self.assertEqual(consumer.polling_wait_time_ms, 1000)

    def test_invalid_batch_size(self):
        with self.assertRaisesRegex(
            ValueError, "Batch size should be between 1 and 10, both inclusive"
        ):
            SimpleSQSConsumer(queue_url=self.queue_url, batch_size=11)
